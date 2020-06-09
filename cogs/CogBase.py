from typing import Type

from discord.ext.commands import Cog, Bot
from core.Latte import Latte


class CogBase(Cog):
    @property
    def bot(self) -> Latte:
        return self._bot

    @bot.setter
    def bot(self, bot: Latte):
        self._bot = bot

    def __init__(self, bot: Latte):
        bot.logger.info(msg=f"Registering the Cog `{self.qualified_name}`")
        self.bot = bot

    def cog_unload(self):
        self.bot.logger.info(msg=f"Unloading the Cog `{self.qualified_name}`")

    def cog_before_invoke(self, ctx):
        self.bot.logger.info(msg=f"Unloading the Cog `{self.qualified_name}`")
        pass

    def cog_after_invoke(self, ctx):
        pass

    def cog_check(self, ctx):
        pass

    def cog_command_error(self, ctx, error):

        pass