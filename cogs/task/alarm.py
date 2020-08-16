from typing import Type
from discord.ext.commands import Bot

from cogs.CogBase import CogBase
from core import Latte


class Alarm(CogBase, name="알람"):
    def __init__(self, bot):
        super().__init__(bot=bot)

    def cog_unload(self):
        pass


def setup(bot: Latte):
    print(f"[Latte] Registering the cog `Alarm`")
    bot.add_cog(cog=Alarm(bot=bot))




