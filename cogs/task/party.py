from typing import List
from core import Latte
from discord import Member
from discord import utils
from discord.ext import commands
from CogBase import CogBase
from utils.tools import EmbedFactory


class PartyCog(CogBase):
    @commands.group(
        name="party",
        description="party commands",
        aliases=["파티"]
    )
    async def party(self, ctx: commands.Context):
        await ctx.send(content="Party module is under construction!")
        
    @party.command(
        name="create",
        description="create new party",
        aliases=["생성"]
    )
    async def create(self, ctx: commands.Context, party_name: str, party_desc: str, party_time: str):
        embedFactory = EmbedFactory(
            title=f"Party : {party_name}",
            description=party_desc,
            color=self.bot.initial_color
        )
        await embedFactory.add_field(name="Time", value=party_time)
        await ctx.send(content="Successfully created new party!", embed=await embedFactory.build())


class Player:
    @property
    def id(self) -> int:
        return self._id

    def __init__(self, **attrs):
        self._id = attrs.pop("id") if "id" in attrs.keys() else 0

    def get_user(self, members: List[Member]) -> Member:
        return utils.find(lambda m: m.id == self.id, members)

    
class Party:
    @property
    def players(self) -> List[Player]:
        return self._players

    def __init__(self, **attrs):
        self._players = attrs.pop("players") if "players" in attrs.keys() else 0




def setup(bot: Latte):
    print(f"[Latte] Registering the cog `Alarm`")
    bot.add_cog(cog=PartyCog(bot=bot))