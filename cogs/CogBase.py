"""
author : Lapis0875 (Github)
date : (KR) 2020-07-06
"""
from discord.ext.commands import Cog, Context
from core.Latte import Latte
from utils.tools import parse_traceback


class CogBase(Cog):
    """
    Base of all Cogs used in latte. This class overrides all Cog methods with basic loggin info.
    """
    @property
    def bot(self) -> Latte:
        """
        Make :bot: variable as property
        :return: a instance of :class Latte:
        """
        return self._bot

    @bot.setter
    def bot(self, bot: Latte):
        """
        Set class`s :property bot:`s value to :param bot:
        :param bot: a instance of :class Latte:
        """
        self._bot = bot

    def __init__(self, bot: Latte):
        """
        Initialize Cog instance.
        :param bot: a instance of :class Latte:
        """
        bot.logger.info(msg=f"Registering the Cog `{self.qualified_name}`")
        self._bot = bot

    def cog_unload(self):
        """
        This method is called when the Cog is being unloaded. This process espicially contains Data saving, closing services, etc.
        """
        self.bot.logger.info(msg=f"Unloading the Cog `{self.qualified_name}`")

    def bot_check(self, ctx):
        self.bot.logger.info(msg=f"[Cog.{self.qualified_name}] [bot_check] Checking the context `{ctx.message.content}`")
        return True

    def bot_check_once(self, ctx):
        self.bot.logger.info(msg=f"[Cog.{self.qualified_name}] [bot_check_once] Checking the context `{ctx.message.content}`")
        return True

    async def cog_before_invoke(self, ctx: Context):
        """
        This coroutine method is called before when the Cog is invoked.
        :param ctx: a instance of :class Context: which contains context info of the invoked Cog.
        """
        self.bot.logger.debug(msg=f"[Cog.{self.qualified_name}] Invoking the context `{ctx.message.content}`")

    async def cog_after_invoke(self, ctx: Context):
        """
        This coroutine method is called after when the Cog is invoked.
        :param ctx: a instance of :class Context: which contains context info of the invoked Cog.
        """
        self.bot.logger.debug(msg=f"[Cog.{self.qualified_name}] Invoked the context `{ctx.message.content}`")

    async def cog_check(self, ctx: Context):
        self.bot.logger.info(msg=f"[Cog.{self.qualified_name}] [cog_check] Checking the context `{ctx.message.content}`")
        return True

    async def cog_command_error(self, ctx: Context, error: Exception):
        self.bot.logger.error(msg=f"Caught an exception during executing context `{ctx.message.content}`")
        parse_traceback(exception=error)