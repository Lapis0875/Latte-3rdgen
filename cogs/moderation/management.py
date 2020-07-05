import json
from typing import Union

import discord
from discord.ext import commands

# import for type hint :
from discord.utils import get, find

from core.Latte import Latte


class Management(commands.Cog):
    bot: Latte = None

    def __init__(self, bot: Latte):
        self.bot: Latte = bot
        self.bot.logger.info("[cogs] Management 모듈을 초기화합니다.")

    def cog_unload(self):
        self.bot.logger.info("[cogs] Management 모듈이 언로드됩니다...")

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        pass

    # Commands
    @commands.group(name="manage",
                    description="서버 관리 기능을 제공하는 명령어 그룹입니다.",
                    aliases=["관리", "management"])
    async def manage(self, ctx: commands.Context):
        """
        서버 관리 기능을 제공하는 명령어 그룹입니다.
        """
        self.bot.logger.info(f'[cogs] [management] {ctx.author} 유저가 {ctx.command} 명령어를 사용했습니다!')
        if ctx.invoked_subcommand is None:
            await ctx.send("서버 관리 명령어입니다. 사용 가능한 명령어들은 `라떼야 도움말 management` 명령어로 확인해주세요!")
        else:
            pass

    @commands.has_guild_permissions(administrator=True)
    @manage.command(name="kick",
                    description="멘션한 유저를 추방합니다.",
                    aliases=["추방"])
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        await member.kick(reason=reason)
        kick_embed = discord.Embed(title="**킥**", description=f"*{member.mention} 님이 킥 처리되었습니다.*")
        kick_embed.add_field(name="**사유**", value=f"*{reason}*", inline=False)

        await ctx.send(embed=kick_embed)

    @commands.has_guild_permissions(administrator=True)
    @manage.command(name="ban",
                    description="멘션한 유저를 차단합니다.",
                    aliases=["차단"])
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        await member.ban(reason=reason)
        ban_embed = discord.Embed(title="**밴**", description=f"*{member.mention} 님이 밴 처리되었습니다.*")
        ban_embed.add_field(name="**사유**", value=f"*{reason}*", inline=False)

        await ctx.send(embed=ban_embed)

    @commands.has_guild_permissions(administrator=True)
    @manage.command(name="pardon",
                    description="멘션한 유저의 차단을 해제합니다.",
                    aliases=["차단해제", "언밴", "unban"])
    async def pardon(self, ctx: commands.Context, id, *, reason: str = None):
        ban_entries: list = await ctx.guild.bans()
        target_ban_entry: discord.guild.BanEntry = discord.utils.find(lambda be: be.user.id == id, ban_entries)

        await ctx.guild.unban(target_ban_entry.user, reason=reason)
        unban_embed = discord.Embed(title="**언밴**", description=f"*{target_ban_entry.user.mention} 님이 밴 해제 처리되었습니다.*")
        unban_embed.add_field(name="**사유**", value=f"*{reason}*", inline=False)

        await ctx.send(embed=unban_embed)

    @commands.has_guild_permissions(administrator=True)
    # @commands.has_guild_permissions(manage_messages=True)
    @manage.command(name="clean-message",
                    description="주어진 개수만큼 해당 채널에서 메세지를 삭제합니다.",
                    aliases=["채팅청소", "clean-msg", "cm"])
    async def clean_msg(self, ctx: commands.Context, amount: int = 5):
        if amount < 1:
            return await ctx.send(f"{amount} 는 너무 적습니다!")

        await ctx.send(content=f"> 🌀 {amount} 개의 메세지를 삭제합니다!")

        del_msgs: list = await ctx.channel.purge(limit=amount+1)
        count: int = len(del_msgs)
        purge_embed = discord.Embed(title="채팅 청소기 🌀", description=f"채팅창을 청소했습니다. {count}개의 메세지를 삭제했습니다.")

        await ctx.send(embed=purge_embed)


def setup(bot: Latte):
    bot.logger.info('[cogs] Management 모듈의 셋업 단계입니다!')
    bot.add_cog(Management(bot))
