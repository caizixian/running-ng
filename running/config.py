from typing import Any, Dict, Union
import yaml
from running.benchmark import JavaBenchmarkSuite
from running.jvm import JVM
from running.modifier import Modifier
from pathlib import Path
import functools
import copy
import logging


def load_class(cls, config):
    return {k: cls.from_config(k, v) for (k, v) in config.items()}


KEY_CLASS_MAPPING = {
    "suites": JavaBenchmarkSuite,
    "modifiers": Modifier,
    "jvms": JVM
}


class Configuration(object):
    def __init__(self, kv_pairs: Dict[str, Any]):
        assert "includes" not in kv_pairs
        assert "overrides" not in kv_pairs
        self.__items = kv_pairs

    def resolve_class(self):
        """Resolve the values by instantiating instances of classes

        For example, self.values["suites"] is a Dict[str, Dict[str, str]],
        where in the inner dictionary contains the string representation of a
        benchmark suite.
        After this function returns, self.values["suites"] becomes a 
        Dict[str, BenchmarkSuite].

        Change the KEY_CLASS_MAPPING to change which classes get resolved.
        """
        for cls_name, cls in KEY_CLASS_MAPPING.items():
            if cls_name in self.__items:
                self.__items[cls_name] = load_class(
                    cls, self.__items[cls_name])
        if "benchmarks" in self.__items:
            for suite_name, bms in self.__items["benchmarks"].items():
                suite = self.__items["suites"][suite_name]
                benchmarks = []
                for b in bms:
                    benchmarks.append(suite.get_benchmark(b))
                self.__items["benchmarks"][suite_name] = benchmarks

    def get(self, name: str) -> Any:
        return self.__items.get(name)

    def override(self, selector: str, new_value: Any):
        current: Any  # Union[Dict[str, Any], List[Any]]
        current = self.__items
        parts = list(selector.split("."))
        for index, p in enumerate(parts):
            if index == len(parts) - 1:
                if p.isnumeric():
                    current[int(p)] = new_value
                else:
                    current[p] = new_value
            else:
                if p.isnumeric():
                    current = current[int(p)]
                else:
                    current = current[p]

    def combine(self, other: "Configuration") -> "Configuration":
        """Combine top-level items of self.values.

        Arrays are concatenated and dictionaries are updated.
        """
        new_values = copy.deepcopy(self.__items)
        for k, v in other.__items.items():
            if k in new_values:
                if type(new_values[k]) is list:
                    new_values[k].extend(copy.deepcopy(other.__items[k]))
                else:
                    assert type(new_values[k]) is dict
                    new_values[k].update(copy.deepcopy(other.__items[k]))
            else:
                new_values[k] = copy.deepcopy(other.__items[k])
        return Configuration(new_values)

    @staticmethod
    def from_file(path: Path) -> "Configuration":
        logging.info("Loading config {}".format(path))
        with path.open("r") as fd:
            config = yaml.safe_load(fd)
        if "includes" in config:
            includes = [Configuration.from_file(
                path.parent.joinpath(p)) for p in config["includes"]]
            base = functools.reduce(
                lambda left, right: left.combine(right), includes)
            if "overrides" in config:
                for selector, new_value in config["overrides"].items():
                    base.override(selector, new_value)
                del config["overrides"]
            del config["includes"]
            final_config = Configuration(config)
            final_config = base.combine(final_config)
        else:
            final_config = Configuration(config)
        return final_config
