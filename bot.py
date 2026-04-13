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

# -----------------------
# KICK
# -----------------------
@bot.tree.command(name="kick", description="Wyrzuć użytkownika")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Brak powodu"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 Wyrzucono {member} | Powód: {reason}")

# -----------------------
# BAN
# -----------------------
@bot.tree.command(name="ban", description="Zbanuj użytkownika")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Brak powodu"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"🔨 Zbanowano {member} | Powód: {reason}")

# -----------------------
# UNBAN
# -----------------------
@bot.tree.command(name="unban", description="Odbanuj użytkownika")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_id: str):
    user = await bot.fetch_user(int(user_id))
    await interaction.guild.unban(user)
    await interaction.response.send_message(f"✅ Odbanowano {user}")

# -----------------------
# MUTE (timeout)
# -----------------------
@bot.tree.command(name="mute", description="Wycisz użytkownika (minuty)")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int):
    duration = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
    await member.edit(timed_out_until=duration)
    await interaction.response.send_message(f"🔇 Wyciszono {member} na {minutes} min")

# -----------------------
# UNMUTE
# -----------------------
@bot.tree.command(name="unmute", description="Odmutuj użytkownika")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    await member.edit(timed_out_until=None)
    await interaction.response.send_message(f"🔊 Odmutowano {member}")

# -----------------------
# WARN SYSTEM
# -----------------------
@bot.tree.command(name="warn", description="Daj warna")
@app_commands.checks.has_permissions(kick_members=True)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "Brak powodu"):
    user_id = member.id

    if user_id not in warns:
        warns[user_id] = []

    warns[user_id].append(reason)

    await interaction.response.send_message(
        f"⚠️ {member.mention} dostał warna!\nPowód: {reason}\nŁącznie warnów: {len(warns[user_id])}"
    )

# -----------------------
# CHECK WARNS
# -----------------------
@bot.tree.command(name="warns", description="Sprawdź warny użytkownika")
async def check_warns(interaction: discord.Interaction, member: discord.Member):
    user_id = member.id
    lista = warns.get(user_id, [])

    if not lista:
        await interaction.response.send_message("Brak warnów ✅")
        return

    await interaction.response.send_message(
        f"⚠️ Warny {member.mention}:\n" + "\n".join(lista)
    )

bot.run(os.getenv("TOKEN_DISCORD"))
