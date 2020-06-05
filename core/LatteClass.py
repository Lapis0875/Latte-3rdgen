import discord
from discord.ext.commands import AutoShardedBot
import sqlite3


class Latte(AutoShardedBot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
