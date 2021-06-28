from typing import Any, Dict
from pathlib import Path
import logging
from running.util import register


class JVM(object):
    CLS_MAPPING: Dict[str, Any]
    CLS_MAPPING = {}

    def __init__(self, **kwargs):
        self.CLS_MAPPING[self.__class__.__name__] = self.__class__
        self.name = kwargs["name"]

    @staticmethod
    def from_config(name: str, config: Dict[str, str]) -> Any:
        return JVM.CLS_MAPPING[config["type"]](name=name, **config)

    def get_executable(self) -> Path:
        raise NotImplementedError

    def __str__(self):
        return "JVM {}".format(self.name)


@register(JVM)
class OpenJDK(JVM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.release = kwargs["release"]
        self.home: Path
        self.home = Path(kwargs["home"])
        if not self.home.exists():
            logging.warn("OpenJDK home {} doesn't exist".format(self.home))
        self.executable = self.home / "bin" / "java"
        if not self.executable.exists():
            logging.warn(
                "{} not found in OpenJDK home".format(self.executable))

    def get_executable(self) -> Path:
        return self.executable

    def __str__(self):
        return "{} OpenJDK {} {}".format(super().__str__(), self.release, self.home)


@register(JVM)
class JikesRVM(JVM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.home: Path
        self.home = Path(kwargs["home"])
        if not self.home.exists():
            logging.warn("JikesRVM home {} doesn't exist".format(self.home))
        self.executable = self.home / "rvm"
        if not self.home.exists():
            logging.warn(
                "{} not found in JikesRVM home".format(self.executable))

    def get_executable(self) -> Path:
        return self.executable

    def __str__(self):
        return "{} JikesRVM {} {}".format(super().__str__(), self.release, self.home)
