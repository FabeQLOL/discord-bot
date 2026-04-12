print("BOT STARTED")

import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")

@bot.command()
async def hej(ctx):
    await ctx.send("Siema 😎")

@bot.command()
async def losuj(ctx):
    import random
    liczba = random.randint(1, 100)
    await ctx.send(f"Wylosowałem: {liczba}")

bot.run(os.getenv("DISCORD_TOKEN"))
