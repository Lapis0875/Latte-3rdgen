from typing import Iterable, Callable, NoReturn, Mapping, List
from .tools import parse_traceback
import os


def recursive_container_loop(task: Callable[[object], object]) -> Callable[[Iterable], NoReturn]:
    def wrrapped_func(cls, container: Iterable):
        for content in container:

            print(f"content `{content}` in container `{container}`")
            # Simple Container
            if issubclass(content.__class__, (list, tuple, set)):
                wrrapped_func(cls, container=content)
            elif issubclass(content.__class__, dict):
                wrrapped_func(cls, container=container.keys())
            else:
                try:
                    task(self=cls, cog_name=content)
                except Exception as e:
                    parse_traceback(exception=e)

    return wrrapped_func


def recursive_cog_loop(task: Callable[[object, str], NoReturn]) -> Callable[[List[str]], NoReturn]:
    def wrrapped_func(cls, dir: str, exclude: List[str] = ['']):
        for file in os.listdir(dir):
            print(f"file `{file}` in directory `{dir}`")
            print(f"checking file`s .py extension : {file[-3:]}")
            if file[-3:] == ".py" and file not in exclude:
                try:
                    raw_cog_name: str = f"{dir}/{file[:-3]}".replace('.', '').replace('/', '', 1)
                    print(raw_cog_name)
                    cog_name: str = raw_cog_name.replace('/', '.')
                    print(cog_name)
                    task(cls, cog_name)
                except Exception as e:
                    parse_traceback(exception=e)
            elif '.' not in file and '__' not in file:
                wrrapped_func(cls=cls, dir=f"{dir}/{file}")
            else:
                continue

    return wrrapped_func
