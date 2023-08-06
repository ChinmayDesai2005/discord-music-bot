import discord
from discord.ext import commands
import music
import asyncio

TOKEN = "INSERT_DISCORD_TOKEN_HERE"

cogs = ["music"]
intents = discord.Intents.all()
client = commands.Bot(command_prefix = "~", intents = intents)

@client.event
async def on_ready():
    print("Bot Online!")

async def load():
    for cog in cogs:
        await client.load_extension(cog)


async def main():
    await load()
    await client.start(TOKEN)
    

asyncio.run(main())
