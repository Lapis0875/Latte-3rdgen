import argparse
from core import Latte

# Create the parser
my_parser = argparse.ArgumentParser(
    prog="Latte",
    description="Latte Bot`s advanced CLI options parser.",
    usage=f"%(prog)s [options]"
)


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
        raise argparse.ArgumentTypeError(msg)


def main():
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

    @bot.event
    async def on_ready():
        bot.logger.info(msg=f"Latte bot has been logged in with {'Test Account' if bot.test_mode else 'Official Account'}")

    bot.run()


main()