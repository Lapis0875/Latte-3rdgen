import traceback
from discord import Embed, Color, Colour
from typing import Type, NoReturn, Dict, Tuple, List
from argparse import ArgumentTypeError


def cast_to_bool(arg: str):
    # True case
    if arg in ["True", "true", "1"]:
        return True

    # False case
    elif arg in ["False", "false", "0"]:
        return False

    # Not suitable args
    else:
        msg = f"Cannot cast an argument `{arg}` into boolean : Not a boolean indicator"
        raise ArgumentTypeError(msg)


def parse_traceback(exception: Exception) -> NoReturn:
    print("Exception details :")
    print(exception.with_traceback(exception.__traceback__))
    print("Traceback details :")
    traceback_list = traceback.extract_tb(exception.__traceback__).format()
    for tb in traceback_list:
        print(tb)


