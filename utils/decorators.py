from typing import Iterable, Callable, NoReturn, Mapping, List, Any, Optional

from discord.ext import commands
from .tools import parse_traceback
import os


def recursive_container_loop(task: Callable) -> Callable[[Iterable], NoReturn]:

    def wrrapped_func(cls, container: Iterable):
        for content in container:

            print(f"content `{content}` in container `{container}`")
            # Simple Container
            if issubclass(content.__class__, (list, tuple, set)):
                wrrapped_func(cls, container=content)
            elif issubclass(content.__class__, dict):
                wrrapped_func(cls, container=container.keys())
            else:
                task(cls, content)

    return wrrapped_func


def surpress_exceptions(func: Callable) -> Callable[[Any], NoReturn]:
    def wrapper_func(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            parse_traceback(exception=e)

    return wrapper_func


def recursive_cog_loop(task: Callable[[object, str], NoReturn]) -> Callable[[object, str, Optional[List[str]]], NoReturn]:
    def wrrapper_func(cls, dir: str, exclude: List[str] = ['']):
        for file in os.listdir(dir):
            print(f"file `{file}` in directory `{dir}`")
            print(f"checking file`s .py extension : {file[-3:]}")
            if file[-3:] == ".py" and file not in exclude:
                raw_cog_name: str = f"{dir}/{file[:-3]}".replace('.', '').replace('/', '', 1)
                print(raw_cog_name)
                cog_name: str = raw_cog_name.replace('/', '.')
                print(cog_name)
                task(cls, cog_name)
            elif '.' not in file and '__' not in file:
                wrrapper_func(cls=cls, dir=f"{dir}/{file}")
            else:
                continue

    return wrrapper_func


def surpress_cog_exceptions(func: Callable[[Any], NoReturn]) -> Callable[[Any], NoReturn]:
    def wrapper_func(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except commands.errors.ExtensionNotFound as e:
            print(f"Cannot find the Cog `{e.name}`")
            parse_traceback(exception=e)

        except commands.errors.ExtensionNotLoaded as e:
            print(f"The Cog `{e.name}` is not loaded.")
            parse_traceback(exception=e)

        except commands.errors.ExtensionAlreadyLoaded as e:
            print(f"The Cog `{e.name}` is already loaded.")
            parse_traceback(exception=e)

        except commands.errors.NoEntryPointError as e:
            print(f"The Cog `{e.name}` does not have setup() function.")
            parse_traceback(exception=e)

        except commands.errors.ExtensionFailed as e:
            print(f"An Exception occured during executing setup() function of the Cog `{e.name}`.")
            parse_traceback(exception=e)
            print(f"Original Exception occured in the extension {e.name}`s setup() : {e.original}")
            parse_traceback(exception=e.original)

        except Exception as e:
            print(f"Unexpected Exception occured during loading the Cog.")
            parse_traceback(exception=e)

    return wrapper_func
