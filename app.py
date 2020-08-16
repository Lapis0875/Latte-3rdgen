import argparse
from core import Latte
from utils import cast_to_bool


def main():
    # Create the parser
    my_parser = argparse.ArgumentParser(
        prog="Latte",
        description="Latte Bot`s advanced CLI options parser.",
        usage=f"%(prog)s [options]"
    )

    my_parser.add_argument(
        "--test", "-t",
        dest="test",
        type=cast_to_bool,
        help="Boolean value which indicates if the bot is starting as test mode.",
        required=True
    )

    args: argparse.Namespace = my_parser.parse_args()
    print(f"Caught CLI arguments : {args}")

    bot = Latte(
        test_mode=args.test,
        description="카페라테를 좋아하는 개발자가 만든 디스코드 봇이에요!",
        help_command=None
    )

    bot.run()

    if bot.check_reboot():
        import sys, os
        excutable = sys.executable
        sys_args = sys.argv[:]
        print(f"System arguments : {sys_args}")
        args.insert(0, excutable)
        print(f"Executing cmd command with arguments ` {sys_args} `")
        os.execv(sys.executable, sys_args)


main()