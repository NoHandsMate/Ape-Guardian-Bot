
import os
import asyncio

import discord
import youtube_dl

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
ADMIN_ID = os.getenv('ADMIN_ID')
# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, download_=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=stream))        

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0] 
        

        if data['duration'] > 300 and download_ == False:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            stream = True
        elif data['duration'] > 300 and download_:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            stream = True
        elif data['duration'] < 300 and download_:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=True))
            stream = False
        else:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            stream = True
       
        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        self.filter = True  # We need to filter the messages?
        self.queue = []
        self.queue_ptr = 0
    
    async def __filter_title(self, ctx, title) -> bool:
        title_ = title.lower()
        new_title = "".join(title_.split())
        
        print(new_title)

        forbidden_words = ["earrape", "timpani", "super suono", "loudest", "ear",
                           "high", "pitch", "alta frequenza", "rumoroso", "frequency",
                           "painful", "extremely"]
        
        for item in forbidden_words:
            if item in new_title:
                await ctx.send('Ci hai provato {0}'.format(ctx.message.author.mention))
                return False
               
        return True   
    
    async def __filter_message(self, ctx) -> bool:
        message = ctx.message.content.lower()
        new_message = "".join(message.split())

        print(new_message)

        forbidden_words = ["earrape", "timpani", "super suono", "loudest", "ear",
                           "high", "pitch", "alta frequenza", "rumoroso", "frequency",
                           "painful", "extremely"]
        for item in forbidden_words:
            if item in new_message:
                await ctx.send('Ci hai provato {0}'.format(ctx.message.author.mention))
                return False

        return True

           
    @commands.command()
    async def yt(self, ctx, *, url):
        """Riproduce un video da yt scaricandolo"""    #TODO Update the "aiuto" command using those strings in function
        
        if self.filter:
            if await self.__filter_message(ctx) == False:
                return

        async with ctx.typing():

            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=False, download_=True)

            if self.filter:
                if await self.__filter_title(ctx, player.title) == False:
                    return

            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def play(self, ctx, *, url):
        """Riproduce un video da yt senza scaricarlo"""
        
        if self.filter:
            if await self.__filter_message(ctx) == False:
                return

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=False, download_=False)

            if self.filter:
                if await self.__filter_title(ctx, player.title) == False:
                    return
                
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Modifica il volume del bot"""
        
        if volume > 300:
            return await ctx.send("Massimo 300 tonno.")
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """Stoppa e disconnette il bot dal canale vocale"""

        await ctx.voice_client.disconnect()
    
    @commands.command()
    async def pause(self, ctx):
        
        """ Mette in pausa il bot """
        
        ctx.voice_client.pause()
    
    @commands.command()
    async def resume(self, ctx):
        
        """Riprende la riproduzione del bot"""
        
        ctx.voice_client.resume()

    @commands.command()
    async def filtra(self, ctx):
        """ Abilità il filtro sulla ricerca di canzoni"""
        if ctx.message.author == ADMIN_ID:
            if self.filter == False:
                self.filter = True
                await ctx.send('Il filtro sulla ricerca di canzoni è stato attivato')
            else:
                self.filter = False
                await ctx.send('Il filtro sulla ricerca di canzoni è stato disattivato')
        else:
            await ctx.send('Non hai il permesso di usare questo comando {0}'.format(ctx.message.author.mention))


    @yt.before_invoke
    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


