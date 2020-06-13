from discord.ext import commands

from CogBase import CogBase
from core import Latte


class Test(CogBase):
    @commands.command(
        name="ping",
        description="Get bot`s latency (checking `HEARTBEAT` and a `HEARTBEAT_ACK`)",
        aliases=["핑"]
    )
    async def ping(self, ctx: commands.Context):
        await ctx.send(content=f"Pong! {round(self.bot.latency * 1000)} (ms)")


def setup(bot: Latte):
    bot.add_cog(Test(bot=bot))