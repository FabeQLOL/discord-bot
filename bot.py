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

@bot.tree.command(name="help", description="Lista komend")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(
        "📜 Dostępne komendy:\n"
        "/hej\n"
        "/losuj\n"
        "/coinflip",
        ephemeral=True
    )
    @bot.tree.command(name="stats", description="Statystyki bota")
async def stats(interaction: discord.Interaction):
    guilds = len(bot.guilds)
    users = sum(g.member_count for g in bot.guilds)
    channels = sum(len(g.channels) for g in bot.guilds)

    await interaction.response.send_message(
        f"""📊 Statystyki bota:

🤖 Serwery: {guilds}
👥 Użytkownicy: {users}
📺 Kanały: {channels}
"""
    )

# 🔐 TOKEN
token = os.getenv("TOKEN_DISCORD")

if not token:
    print("❌ ERROR: Brak tokena!")
else:
    print("BOT STARTED")
    bot.run(token)

