from typing import Iterable, Callable, NoReturn
from .tools import parse_traceback


def recursive_container_loop(task: Callable[[object], object]) -> Callable[[Iterable], NoReturn]:
    def wrrapped_func(container: Iterable):
        for content in container:
            # Simple Container
            if issubclass(list, content) or issubclass(tuple, content) or issubclass(set, content):
                wrrapped_func(container=content)
            elif issubclass(dict, content):
                wrrapped_func(container=container.keys())
            else:
                try:
                    task(content)
                except Exception as e:
                    parse_traceback(exception=e)

    return wrrapped_func
