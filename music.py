import discord
from discord import FFmpegOpusAudio
from discord.ext import commands
from discord.utils import get
import youtube_dl
import datetime
import random
import asyncio
import json

songQueue = {}
songPlaying = True
isPaused = False
info = None

class music(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music COG ready!")


    def getInfo(self, info):
        try:
            url = info['url']
            title = info['title']
            id = info['id']
            duration = info['duration']
            return {'url': url, 'title': title, 'id': id, 'duration': duration}
        except:
            if '_type' == 'playlist':
                print("this is a playlist")
    

    @commands.command(aliases=['connect'])
    async def join(self, ctx):
        global isPaused
        isPaused = True
        if ctx.author.voice is None:
            await ctx.send(embed=discord.Embed(description="You are not in any voice channel", color=0x1DB954))
        voice_channel = ctx.author.voice.channel
        if not ctx.voice_client:
            await voice_channel.connect()
            songQueue[ctx.guild.id] = []
            await ctx.channel.send(embed=discord.Embed(description=f"**Joined: ** `{voice_channel}`", color=0x1DB954))
        else:
            await ctx.voice_client.move_to(voice_channel)

    @commands.command(aliases=['leave'])
    async def disconnect(self, ctx):
        global songQueue
        if ctx.voice_client != None:
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            await ctx.channel.send(embed=discord.Embed(description=f"**Disconnected**", color=0x1DB954))
            del(songQueue[ctx.guild.id])
        else:
            await ctx.channel.send(embed=discord.Embed(description="Not connected to any channel", color=0x1DB954))


    def playsong(self, ctx, songurl):
        print("playsong")
        global isPaused, songQueue
        ctx.guild.voice_client.stop()
        # FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        FFMPEG_BEFORE_OPTS = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
        vc = ctx.guild.voice_client
        source = FFmpegOpusAudio(songurl, before_options=FFMPEG_BEFORE_OPTS)
        def after_playing(err):
            print("song ended")
            if len(songQueue[ctx.guild.id]) > 1:
                print("doing next song")
                self.playsong(ctx, songurl=songQueue[ctx.guild.id][1]['url'])
                songQueue[ctx.guild.id].pop(0)
            else:
                songQueue[ctx.guild.id].pop(0)
        
        vc.play(source, after=after_playing)

    def addToQueue(self, ctx, songurl):
        pass

    def get_name(self, message):
        name = message.replace("~play ", "", 1)
        name = message.replace("~play", "", 1)
        return name
    
    def getDuration(self, duration):
        conversion = datetime.timedelta(seconds=duration)
        return conversion

    @commands.command()
    async def play(self, ctx, url=None):
        global songQueue, info
        message = ctx.message.content
        message_splitted = message.split(" ")
        mes_len = len(message_splitted)
        YDL_OPTIONS= {'format':'bestaudio', 'cachedir':False, 'no-playlist':True,}
        if ctx.message.guild.voice_client:
            if url != None:
                try:
                    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                        info = ydl.extract_info(url, download=False)
                        info = self.getInfo(info)
                        if len(songQueue[ctx.guild.id]) > 0:
                            songQueue[ctx.guild.id].append(info)
                            await ctx.channel.send(embed=discord.Embed(description=f"`{info['title']}` added to **Queue**.", color=0x1DB954))
                        elif len(songQueue[ctx.guild.id]) == 0:
                            songQueue[ctx.guild.id].append(info)
                            songQueue[ctx.guild.id][0]['url']
                            self.playsong(ctx, songQueue[ctx.guild.id][0]['url'])
                            await ctx.channel.send(embed=discord.Embed(title="Playing:", description=f"`{info['title']}`", color=0x1DB954))
                        else:
                            await ctx.channel.send(embed=discord.Embed(description="Something Went Wrong!", color=0x1DB954))
                except Exception as e:
                    print(e)
                    vid_name = self.get_name(message)
                    searching_yt = await ctx.channel.send(embed=discord.Embed(title="Searching YouTube:", description=f'**{vid_name}**', color=0x1DB954))
                    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                        info = ydl.extract_info(f"ytsearch:{vid_name}", download=False)
                        info = self.getInfo(info['entries'][0])
                        # print(info)
                        if len(songQueue[ctx.guild.id]) > 0:
                            songQueue[ctx.guild.id].append(info)
                            queueStatus = "Added to Queue: "
                        elif len(songQueue[ctx.guild.id]) == 0:
                            songQueue[ctx.guild.id].append(info)
                            queueStatus = "Playing: "
                            self.playsong(ctx, songQueue[ctx.guild.id][0]['url'])
                        else:
                            await ctx.channel.send(embed=discord.Embed(description="Something Went Wrong!", color=0x1DB954))
                        await searching_yt.edit(embed=discord.Embed(title=queueStatus, description=f"**[{info['title']}](https://www.youtube.com/watch?v={info['id']})**", color=0x1DB954))
            else:
                await ctx.channel.send(embed=discord.Embed(title="Invalid Syntax:", description="**Syntax**:`~play [URL or Video Name]`", color=0x1DB954))
        else:
            await ctx.channel.send(embed=discord.Embed(description="The Bot is not in a voice channel!\nUse `~join` to make the bot join. ", color=0x1DB954))

    @commands.command()
    async def clear(self, ctx):
        global songQueue
        try:  
            songQueue[ctx.guild.id] = [songQueue[ctx.guild.id][0]]
            await ctx.channel.send(embed=discord.Embed(title=f"**Queue Cleared**", color=0x1DB954))
        except:
            await ctx.channel.send("Something went wrong!")

    @commands.command(aliases=['stop'])
    async def pause(self, ctx):
        if ctx.message.guild.voice_client.is_playing():
            ctx.message.guild.voice_client.pause()
            await ctx.channel.send(embed=discord.Embed(title="**Paused**", color=0x1DB954))
        else:
            await ctx.channel.send(embed=discord.Embed(title="Nothing to Pause", color=0x1DB954))
    
    @commands.command(aliases=['start'])
    async def resume(self, ctx):
        global isPaused
        if ctx.message.guild.voice_client.is_paused():
            ctx.message.guild.voice_client.resume()
            await ctx.channel.send(embed=discord.Embed(title="**Resumed**", color=0x1DB954))
        else:
            await ctx.channel.send(embed=discord.Embed(title="Player Already Resumed", color=0x1DB954))
    
    @commands.command()
    async def song(self, ctx):
        global songQueue
        if len(songQueue[ctx.guild.id]) == 0 or not ctx.message.guild.voice_client.is_playing:
            await ctx.channel.send(embed=discord.Embed(title="Nothing Playing Right Now", color=0x1DB954))
        else:
            await ctx.channel.send(embed=discord.Embed(title='**Now Playing**:', description=f'`{songQueue[ctx.guild.id][0]["title"]}`', color=0x1DB954))

    @commands.command(aliases=['next'])
    async def skip(self, ctx, number=None):
        global songQueue
        if number == None or int(number) == 1:
            try:
                ctx.message.guild.voice_client.stop()
                await ctx.channel.send(embed=discord.Embed(title="Skipped", color=0x1DB954))
            except Exception as e:
                if songQueue[ctx.guild.id]:
                    await ctx.channel.send(embed=discord.Embed(title="Skipped", color=0x1DB954))
                else:
                    await ctx.channel.send(embed=discord.Embed(title="Nothing in Queue", color=0x1DB954))
        else:
            try:
                if int(number) > 1 and int(number) <= len(songQueue[ctx.guild.id]):
                    name = songQueue[ctx.guild.id].pop(int(number) - 1)
                    await ctx.channel.send(embed=discord.Embed(description=f"Skipped `{name['title']}`", color=0x1DB954))
                else:
                    await ctx.channel.send(embed=discord.Embed(description=f"Number not in Queue!", color=0x1DB954))
            except Exception as e:
                print(e)
                await ctx.channel.send(embed=discord.Embed(description=f"Invalid Input:\n`Enter a valid number.`", color=0x1DB954))


    @commands.command()
    async def skipnext(self, ctx):
        global songQueue
        try:
            songQueue[ctx.guild.id].pop(1)
            await ctx.channel.send(embed=discord.Embed(title="Skipped Next Song", color=0x1DB954))
        except Exception as e:
            print(e)
            await ctx.channel.send(embed=discord.Embed(title="Nothing Next!", color=0x1DB954))
    
    @commands.command()
    async def queue(self, ctx):
        global songQueue
        queuelist = ""
        for idx, song in enumerate(songQueue[ctx.guild.id]):
            if idx == 0:
                queuelist = queuelist + f"**{idx+1}**. `{song['title']} ({self.getDuration(song['duration'])})` - **Now Playing**\n"
            else:
                queuelist = queuelist + f"**{idx+1}**. `{song['title']} ({self.getDuration(song['duration'])})`\n"
        if queuelist:
            await ctx.channel.send(embed=discord.Embed(title="Queue:", description=queuelist, color=0x1DB954))
        else:
            await ctx.channel.send(embed=discord.Embed(title="Nothing in Queue", description="Play something with `~play`", color=0x1DB954))

    @commands.command()
    async def shuffle(self, ctx):
        global songQueue
        firstSong = songQueue[ctx.guild.id].pop(0)
        random.shuffle(songQueue[ctx.guild.id])
        songQueue[ctx.guild.id].insert(0, firstSong)
        await ctx.channel.send(embed=discord.Embed(title="Queue Shuffled", color=0x1DB954))
    
    @commands.command()
    async def restart(self, ctx):
        global songQueue
        songQueue[ctx.guild.id].insert(1, songQueue[ctx.guild.id][0])
        ctx.message.guild.voice_client.stop()
        self.after_playing()

    @commands.command()
    async def playlist(self, ctx, url=None):
        global songQueue
        message = ctx.message.content
        message_splitted = message.split(" ")
        mes_len = len(message_splitted)
        YDL_OPTIONS= {'format':'bestaudio', 'cachedir':False, 'yes-playlist':True,}
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ytdl:
            info = ytdl.extract_info(url, download=False)
        print(f"{self.getInfo(info)['url']}")

    async def printQueue(self, ctx):
        global songQueue
        print(songQueue)
async def setup(client):
    await client.add_cog(music(client))

