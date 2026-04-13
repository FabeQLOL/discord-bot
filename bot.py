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
    number = random.randint(1, 100)
    await ctx.send(f"Wylosowałem: {number}")

# START BOTA
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        print("❌ ERROR: Brak tokena!")
    else:
        bot.run(token)
