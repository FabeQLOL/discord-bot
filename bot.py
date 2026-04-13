import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import asyncio

print("BOT STARTED")

intents = discord.Intents.default()
intents.members = True  # WAŻNE do ban/kick/mute

bot = commands.Bot(command_prefix="!", intents=intents)

# ===== READY =====
@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Zsynchronizowano {len(synced)} komend")
    except Exception as e:
        print(e)

# ===== KOMENDY =====

@bot.tree.command(name="hej", description="Powitanie")
async def hej(interaction: discord.Interaction):
    await interaction.response.send_message("Siema 😎")

@bot.tree.command(name="losuj", description="Losuje liczbę 1-100")
async def losuj(interaction: discord.Interaction):
    await interaction.response.send_message(str(random.randint(1, 100)))

@bot.tree.command(name="coinflip", description="Orzeł czy reszka")
async def coinflip(interaction: discord.Interaction):
    wynik = random.choice(["Orzeł 🦅", "Reszka 🪙"])
    await interaction.response.send_message(wynik)

# ===== MODERACJA =====

@bot.tree.command(name="ban", description="Banuje użytkownika")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "Brak powodu"):
    await user.ban(reason=reason)
    await interaction.response.send_message(f"🔨 Zbanowano {user} | Powód: {reason}")

@bot.tree.command(name="kick", description="Wyrzuca użytkownika")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "Brak powodu"):
    await user.kick(reason=reason)
    await interaction.response.send_message(f"👢 Wyrzucono {user} | Powód: {reason}")

@bot.tree.command(name="mute", description="Wycisza użytkownika (timeout)")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, user: discord.Member, minutes: int):
    await user.timeout(discord.utils.utcnow() + discord.timedelta(minutes=minutes))
    await interaction.response.send_message(f"🔇 Wyciszono {user} na {minutes} minut")

# ===== BŁĘDY (np. brak permisji) =====

@ban.error
@kick.error
@mute.error
async def mod_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("❌ Nie masz permisji!", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Wystąpił błąd", ephemeral=True)

# ===== TOKEN =====

token = os.getenv("TOKEN_DISCORD")

if not token:
    print("❌ ERROR: Brak tokena!")
else:
    bot.run(token)
