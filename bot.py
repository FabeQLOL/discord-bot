import discord
from discord.ext import commands
import random
import os

intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Zsynchronizowano {len(synced)} komend")
    except Exception as e:
        print(e)

# 👋 /hej
@bot.tree.command(name="hej", description="Powitanie")
async def hej(interaction: discord.Interaction):
    await interaction.response.send_message("Siema 😎")

# 🎲 /losuj
@bot.tree.command(name="losuj", description="Losuje liczbę")
async def losuj(interaction: discord.Interaction):
    liczba = random.randint(1, 100)
    await interaction.response.send_message(f"🎲 {liczba}")

# 🪙 /coinflip
@bot.tree.command(name="coinflip", description="Rzut monetą")
async def coinflip(interaction: discord.Interaction):
    wynik = random.choice(["Orzeł 🦅", "Reszka 🪙"])
    await interaction.response.send_message(f"🪙 {wynik}")

# 🔐 TOKEN
token = os.getenv("TOKEN_DISCORD")

if not token:
    print("❌ ERROR: Brak tokena!")
else:
    print("BOT STARTED")
    bot.run(token)
