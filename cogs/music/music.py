import math
import re
import lavalink
import discord
from discord.ext import commands, menus
from CogBase import CogBase
from core import Latte
from factories import EmbedFactory

# regex to check the web url.
url_rx = re.compile(r'https?://(?:www\.)?.+')


class Music(CogBase):
    def __init__(self, bot: Latte):
        super().__init__(bot=bot)

        if not hasattr(bot, 'lavalink') or self.bot.lavalink is None:
            # This ensures the client isn't overwritten during cog reloads.
            bot.lavalink = lavalink.Client(user_id=self.bot.user.id if self.bot.user is not None else self.bot.bot_config["id"])
            bot.lavalink.add_node(
                bot.bot_config["lavalink"]["host"],  # Host
                bot.bot_config["lavalink"]["port"],  # Port
                bot.bot_config["lavalink"]["password"],  # Password
                bot.bot_config["lavalink"]["region"]  # Region
            )
            bot.add_listener(bot.lavalink.voice_update_handler, "on_socket_response")
        bot.lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        self.bot.lavalink._event_hooks.clear()
        super().cog_unload()

    async def cog_before_invoke(self, ctx):
        await super().cog_before_invoke(ctx=ctx)
        if guild_check := ctx.guild is not None:
            await self.ensure_voice(ctx)
        return guild_check

    async def ensure_voice(self, ctx: commands.Context):
        """
        Ensure if bot needs to create voice connection.
        :param ctx: a instance of :class Context: which has context information of invoked command.
        """
        # Create player.
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        # Check if bot should connect into voice channel and create player to play music.
        # Bot only needs to connect into voice channel if command is a music command.
        invoked_subcommand_set: set = {command.name for command in ctx.command.invoked_subcommand}
        should_connect = ctx.command.name in ("music", "m") \
                         and ctx.invoked_subcommand \
                         and ("play" in invoked_subcommand_set or "p" in invoked_subcommand_set
                              or "queue" in invoked_subcommand_set or "q" in invoked_subcommand_set)

        ensure_voice_result = EmbedFactory(
            title="라떼의 잔잔한 카페 라디오 🎶",
            description="라떼봇의 음악 기능을 이용해주셔서 감사합니다!"
        )

        if not ctx.author.voice or not ctx.author.voice.channel:
            # User is not connected to voice channel! Can`t find any voice channel to enter, so error occured.
            error_msg: str = "음악을 재생하려면, 우선 음성 채널에 들어가주세요!"

            await ensure_voice_result.add_field(name="오류 발생!", value=error_msg)
            ensure_voice_result.color = self.bot.error_color
            await ctx.send(embed=await ensure_voice_result.build())

            raise commands.CommandInvokeError(error_msg)

        if not player.is_connected:
            # Player is not connected, so we need to create new player.
            if not should_connect:
                # Context shows that command is not the music command. Ignoring player creation.
                error_msg: str = "연결되지 않았어요!"
                await ensure_voice_result.add_field(name="오류 발생!", value=error_msg)
                ensure_voice_result.color = self.bot.error_color
                await ctx.send(embed=await ensure_voice_result.build())
                raise commands.CommandInvokeError(error_msg)

            # Get bot`s permission in target voice channel.
            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect:
                # Bot does not have the permisson to connect to the target voice channel.
                error_msg: str = "음성 채널에 연결하기 위한 권한이 없어요 :("
                await ensure_voice_result.add_field(name="오류 발생!", value=error_msg)
                ensure_voice_result.color = self.bot.error_color
                await ctx.send(embed=await ensure_voice_result.build())
                raise commands.CommandInvokeError(error_msg)

            if not permissions.speak:
                # Bot does not have the permisson to speak in the target voice channel.
                error_msg: str = "음성 채널에서 말하기 위한 권한이 없어요 :("
                await ensure_voice_result.add_field(name="오류 발생!", value=error_msg)
                ensure_voice_result.color = self.bot.error_color
                await ctx.send(embed=await ensure_voice_result.build())
                raise commands.CommandInvokeError(error_msg)

            # Store channel id into player.
            player.store('channel', ctx.channel.id)
            # Connect bot to the voice channel.
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))

        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                error_msg: str = "제가 들어있는 음성 채널에 들어와 주세요!"
                await ensure_voice_result.add_field(name="오류 발생!", value=error_msg)
                ensure_voice_result.color = self.bot.warning_color
                await ctx.send(embed=await ensure_voice_result.build())
                raise commands.CommandInvokeError(error_msg)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)

    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)

    @commands.group(
        name="music",
        description="Command group of music feature.",
        aliases=["m"]
    )
    async def music(self, ctx: commands.Context):
        """
        Group commands for music features.
        :param ctx: a instance of :class Context: which has context information of invoked command.
        """
        pass

    @music.command(
        name="play",
        description="play the given music",
        aliases=['p']
    )
    async def play(self, ctx, *, query: str):
        """
        Play the given music using query.
        :param ctx: a instance of :class Context: which has context information of invoked command.
        :param query: a search url of search query texts to get the music.
        """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id, endpoint=str(ctx.guild.region))
        query = query.strip('<>')

        if not url_rx.match(query):
            query = f'ytsearch:{query}'
        results = await player.node.get_tracks(query)

        if not results or not results['tracks']:
            return await ctx.send('Nothing found!')

        embed = EmbedFactory(color=self.bot.initial_color)
        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']

            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            embed.title = 'Playlist Enqueued!'
            embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
        else:
            track = results['tracks'][0]
            embed.title = 'Track Enqueued'
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
            player.add(requester=ctx.author.id, track=track)
        await ctx.send(embed=embed)
        if not player.is_playing:
            await player.play()

    @music.command()
    async def seek(self, ctx, *, seconds: int):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        track_time = player.position + (seconds * 1000)
        await player.seek(track_time)
        await ctx.send(f'Moved track to **{lavalink.utils.format_time(track_time)}**')

    @music.command(aliases=['forceskip'])
    async def skip(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('Not playing.')
        await player.skip()

    @music.command()
    async def stop(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('Not playing.')
        player.queue.clear()
        await player.stop()

    @music.command(aliases=['np', 'n', 'playing'])
    async def now(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.current:
            return await ctx.send('Nothing playing.')
        position = lavalink.utils.format_time(player.position)
        if player.current.stream:
            duration = '🔴 LIVE'
        else:
            duration = lavalink.utils.format_time(player.current.duration)
        song = f'**[{player.current.title}]({player.current.uri})**\n({position}/{duration})'
        embed = discord.Embed(color=discord.Color.blurple(),
                              title='Now Playing', description=song)
        await ctx.send(embed=embed)

    @music.command(aliases=['q'])
    async def queue(self, ctx, page: int = 1):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.queue:
            return await ctx.send('Nothing queued.')
        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)
        start = (page - 1) * items_per_page
        end = start + items_per_page
        queue_list = ''
        for index, track in enumerate(player.queue[start:end], start=start):
            queue_list += f'`{index + 1}.` [**{track.title}**]({track.uri})\n'
        embed = discord.Embed(colour=discord.Color.blurple(),
                              description=f'**{len(player.queue)} tracks**\n\n{queue_list}')
        embed.set_footer(text=f'Viewing page {page}/{pages}')
        await ctx.send(embed=embed)

    @music.command(aliases=['resume'])
    async def pause(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('Not playing.')
        if player.paused:
            await player.set_pause(False)
            await ctx.send('⏯ | Resumed')
        else:
            await player.set_pause(True)
            await ctx.send('⏯ | Paused')

    @music.command(aliases=['vol'])
    async def volume(self, ctx, volume: int = None):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not volume:
            return await ctx.send(f'🔈 | {player.volume}%')
        await player.set_volume(volume)
        await ctx.send(f'🔈 | Set to {player.volume}%')

    @music.command()
    async def shuffle(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('Nothing playing.')
        player.shuffle = not player.shuffle
        await ctx.send('🔀 | Shuffle ' + ('enabled' if player.shuffle else 'disabled'))

    @music.command(aliases=['loop'])
    async def repeat(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('Nothing playing.')
        player.repeat = not player.repeat
        await ctx.send('🔁 | Repeat ' + ('enabled' if player.repeat else 'disabled'))

    @music.command()
    async def remove(self, ctx, index: int):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.queue:
            return await ctx.send('Nothing queued.')
        if index > len(player.queue) or index < 1:
            return await ctx.send(f'Index has to be **between** 1 and {len(player.queue)}')
        removed = player.queue.pop(index - 1)  # Account for 0-index.
        await ctx.send(f'Removed **{removed.title}** from the queue.')

    @music.command()
    async def find(self, ctx, *, query):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not query.startswith('ytsearch:') and not query.startswith('scsearch:'):
            query = 'ytsearch:' + query
        results = await player.node.get_tracks(query)
        if not results or not results['tracks']:
            return await ctx.send('Nothing found.')
        tracks = results['tracks'][:10]  # First 10 results
        o = ''
        for index, track in enumerate(tracks, start=1):
            track_title = track['info']['title']
            track_uri = track['info']['uri']
            o += f'`{index}.` [{track_title}]({track_uri})\n'
        embed = discord.Embed(color=discord.Color.blurple(), description=o)
        await ctx.send(embed=embed)

    @music.command(aliases=['dc'])
    async def disconnect(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_connected:
            return await ctx.send('Not connected.')
        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.send('You\'re not in my voicechannel!')
        player.queue.clear()
        await player.stop()
        await self.connect_to(ctx.guild.id, None)
        await ctx.send('*⃣ | Disconnected.')


def setup(bot):
    bot.add_cog(Music(bot))
