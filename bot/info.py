from discord.ext import commands

from CogBase import CogBase
from core import Latte
from utils.tools import EmbedFactory


class Info(CogBase):
    @commands.command(
        name="info",
        description="show information of the bot",
        alias=["정보"]
    )
    async def info(self, ctx: commands.Context):
        embed_factory = EmbedFactory(
            title=f"{self.bot.user.name} 의 정보에요!",
            description="",
            color=self.bot.initial_color
        )
        await embed_factory.add_field(name="함께하고있는 서버들", value=f"{len(self.bot.guilds)} 개")
        await embed_factory.add_field(name="함께하고있는 유저들", value=f"{len({u for u in self.bot.users if not u.bot})} 명")
        await embed_factory.add_field(name="함께하고있는 서버들", value=f"{len(self.bot.guilds)} 개")


def setup(bot: Latte):
    bot.add_cog(Info(bot=bot))
