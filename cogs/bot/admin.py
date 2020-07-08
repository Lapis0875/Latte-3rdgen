from discord.ext import commands, menus
import discord
from CogBase import CogBase
from core import Latte


class Adimn(CogBase):
    def __init__(self, bot: Latte):
        super().__init__(bot=bot)

    @commands.is_owner()
    @commands.group(
        name="admin",
        description="",
        aliases=["owner", "어드민"]
    )
    async def admin(self, ctx: commands.Context):
        pass
    
    @admin.command(
        name="stop",
        description="Stop the bot.",
        aliases=["shutdown", "종료"]
    )
    async def stop(self, ctx: commands.Context):
        self.bot.logger.info("봇 종료 명령어가 실행되었습니다!")
        await ctx.send("봇을 종료합니다!")
        self.bot.do_reboot = False
        await self.bot.close()
