import discord
from discord.ext import commands
from discord import app_commands
import os
import random

print("BOT STARTED")

# Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ===== EVENT START =====
@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")
    
    try:
        synced = await bot.tree.sync()
        print(f"Zsynchronizowano {len(synced)} komend slash")
    except Exception as e:
        print(f"Błąd sync: {e}")


# ===== PREFIX COMMANDS =====
@bot.command()
async def hej(ctx):
    await ctx.send("Siema 😎")


@bot.command()
async def losuj(ctx):
    await ctx.send(random.randint(1, 100))


# ===== SLASH COMMANDS =====
@bot.tree.command(name="hej", description="Wita użytkownika")
async def hej_slash(interaction: discord.Interaction):
    await interaction.response.send_message("Siema 😎🔥")


@bot.tree.command(name="losuj", description="Losuje liczbę od 1 do 100")
async def losuj_slash(interaction: discord.Interaction):
    await interaction.response.send_message(str(random.randint(1, 100)))


# ===== RUN BOT =====
token = os.getenv("DISCORD_TOKEN")

if not token:
    print("❌ ERROR: Brak tokena!")
else:
    bot.run(token)
