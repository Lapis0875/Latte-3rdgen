from CogBase import CogBase
from discord.ext import commands
import discord
from sqlite3 import Connection, Cursor


class WarnCog(CogBase):
    """
    Cog for bot`s warn function.
    This function use DataBase to record each user`s warn record.
    """

    @commands.group(
        name="warn",
        description="Group command for warn functions.",
        aliases=["경고"]
    )
    async def warn(self, ctx: commands.Context, member: discord.Member = None):
        if member is not None:
            await self.warn_give(ctx=ctx, member=member)
        pass

    @warn.command(
        name="give",
        description="Warn certain member (Guild-dependant).",
        aliases=["부여"]
    )
    async def warn_give(self, ctx: commands.Context, member: discord.Member):
        guild_db: Connection = await self.bot.connect_db(type="guild")
        guild_db.execute(sql=f'INSERT ? INTO warn-{ctx.guild.id} WHERE id=?', parameters=())
        pass

    @warn.command(
        name="enable",
        description="Enable bot`s Warn function in this guild.",
        aliases=["활성화"]
    )
    async def warn_enable(self, ctx: commands.Context):
        guild_db: Connection = await self.bot.connect_db(type="guild")
        execute_cur: Cursor = guild_db.execute(sql=f'CREATE TABLE IF NOT EXISTS "warning-{ctx.guild.id}"('
                                                   '"id"	INTEGER NOT NULL UNIQUE,'
                                                   '"count" INTERGER NOT NULL,'
                                                   '"date" TEXT NOTNULL,'
                                                   'PRIMARY KEY("id")'
                                                   ') WITHOUT ROWID;')

    @warn.command(
        name="disable",
        description="Disable bot`s Warn function in this guild.",
        aliases=["비활성화"]
    )
    async def warn_disable(self, ctx: commands.Context):
        guild_db: Connection = await self.bot.connect_db(type="guild")
        execute_cur: Cursor = guild_db.execute(sql=f'DROP TABLE IF EXISTS "warning-{ctx.guild.id}"')


def setup(bot):
    bot.add_cog(cog=WarnCog(bot=bot))
