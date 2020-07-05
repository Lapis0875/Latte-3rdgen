from typing import Type

from discord.ext.commands import Cog, Context
from core.Latte import Latte
from utils.tools import parse_traceback


class CogBase(Cog):
    @property
    def bot(self) -> Latte:
        return self._bot

    @bot.setter
    def bot(self, bot: Latte):
        self._bot = bot

    def __init__(self, bot: Latte):
        bot.logger.info(msg=f"Registering the Cog `{self.qualified_name}`")
        self._bot = bot

    def cog_unload(self):
        self.bot.logger.info(msg=f"Unloading the Cog `{self.qualified_name}`")

    def bot_check(self, ctx):
        self.bot.logger.info(msg=f"[Cog.{self.qualified_name}] [bot_check] Checking the context `{ctx.message.content}`")
        return True

    def bot_check_once(self, ctx):
        self.bot.logger.info(msg=f"[Cog.{self.qualified_name}] [bot_check_once] Checking the context `{ctx.message.content}`")
        return True

    async def cog_before_invoke(self, ctx: Context):
        self.bot.logger.info(msg=f"[Cog.{self.qualified_name}] Invoking the context `{ctx.message.content}`")

    async def cog_after_invoke(self, ctx: Context):
        self.bot.logger.info(msg=f"[Cog.{self.qualified_name}] Invoked the context `{ctx.message.content}`")

    async def cog_check(self, ctx: Context):
        self.bot.logger.info(msg=f"[Cog.{self.qualified_name}] [cog_check] Checking the context `{ctx.message.content}`")
        return True

    async def cog_command_error(self, ctx: Context, error: Exception):
        self.bot.logger.info(msg=f"Caught an exception during executing context `{ctx.message.content}`")
        parse_traceback(exception=error)