from typing import List
from CogBase import CogBase
from core import Latte
from discord.ext import commands
import discord
from sqlite3 import Connection, Cursor


class Level(CogBase):
    """
    Cog for bot`s user level function.
    This function use DataBase to record each user`s level record.
    """
    
    def __init__(self, bot: Latte):
        super().__init__(bot=bot)

    @commands.Cog.listener(name="on_command")
    async def msg_levelup(self, message: discord.Message):
        pass


    @commands.group(
        name="level",
        description="Group command for level functions.",
        aliases=["레벨"]
    )
    async def level(self, ctx: commands.Context, member: discord.Member = None):
        pass

    @level.command(
        name="view",
        description="View user`s level (Guild-independant).",
        aliases=["보기"]
    )
    async def level_view(self, ctx: commands.Context, user: discord.User = None):
        user_db: Connection = await self.bot.connect_db(type="users")
        execute_cur: Cursor = user_db.execute(sql=f'SELECT * FROM level WHERE id=?', parameters=((user.id if user is not None else ctx.author.id),))
        execute_result: List = execute_cur.fetchall()

    @commands.has_guild_permissions(administrator=True)
    @level.command(
        name="enable",
        description="Enable bot`s Warn function in this guild.",
        aliases=["활성화"]
    )
    async def level_enable(self, ctx: commands.Context):
        pass


def setup(bot):
    bot.add_cog(cog=Level(bot=bot))