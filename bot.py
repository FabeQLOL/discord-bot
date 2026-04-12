import discord
from discord.ext import commands
import os
import random

print("BOT STARTED")

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
    await ctx.send(random.randint(1, 100))

token = os.getenv("DISCORD_TOKEN")

if token is None:
    print("BRAK TOKENA W ENV!")
else:
    bot.run(token)
