import traceback
from typing import Type, NoReturn


def parse_traceback(exception: Type[Exception]) -> NoReturn:
    print("Exception details :")
    print(exception.with_traceback(exception.__traceback__))
    print("Traceback details :")
    traceback_list = traceback.extract_tb(exception.__traceback__).format()
    for tb in traceback_list:
        print(tb)
