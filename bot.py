import discord
from discord.ext import commands
from discord import app_commands
import random

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# prosta baza warnów (w RAM — resetuje się po restarcie)
warns = {}

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Zalogowano jako {bot.user}")

# -----------------------
# FUN: HEJ
# -----------------------
@bot.tree.command(name="hej", description="Powitaj bota")
async def hej(interaction: discord.Interaction):
    await interaction.response.send_message("Siema 😎")

# -----------------------
# LOSUJ
# -----------------------
@bot.tree.command(name="losuj", description="Losuj liczbę 1-100")
async def losuj(interaction: discord.Interaction):
    await interaction.response.send_message(str(random.randint(1, 100)))

# -----------------------
# COINFLIP
# -----------------------
@bot.tree.command(name="coinflip", description="Orzeł czy reszka")
async def coinflip(interaction: discord.Interaction):
    wynik = random.choice(["Orzeł 🦅", "Reszka 🪙"])
    await interaction.response.send_message(wynik)

bot.run(os.getenv("TOKEN_DISCORD"))
