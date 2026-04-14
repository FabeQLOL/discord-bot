import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import asyncio
import json

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

def load_data():
    try:
        with open("economy.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open("economy.json", "w") as f:
        json.dump(data, f, indent=4)

def get_user(user_id):
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {"money": 100}
        save_data(data)
    return data

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

@bot.tree.command(name="balance", description="Sprawdź swój stan konta 💰")
async def balance(interaction: discord.Interaction):
    data = get_user(interaction.user.id)
    money = data[str(interaction.user.id)]["money"]

    await interaction.response.send_message(f"Masz {money}$ 💰")

@bot.tree.command(name="work", description="Zarabiaj pieniądze 💼")
async def work(interaction: discord.Interaction):
    data = get_user(interaction.user.id)

    zarobek = random.randint(10, 50)
    data[str(interaction.user.id)]["money"] += zarobek

    save_data(data)

    await interaction.response.send_message(f"Zarobiłeś {zarobek}$ 💰")

@bot.tree.command(name="ruletka", description="Zagraj w ruletkę 🎰")
async def ruletka(interaction: discord.Interaction, liczba: int, stawka: int):

    if liczba < 1 or liczba > 36:
        await interaction.response.send_message("Liczba 1-36 ❌", ephemeral=True)
        return

    data = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    if data[user_id]["money"] < stawka:
        await interaction.response.send_message("Nie masz tyle kasy ❌", ephemeral=True)
        return

    wylosowana = random.randint(1, 36)

    if liczba == wylosowana:
        wygrana = stawka * 10
        data[user_id]["money"] += wygrana
        wynik = f"🎉 WYGRAŁEŚ {wygrana}$!"
    else:
        data[user_id]["money"] -= stawka
        wynik = f"😢 Przegrałeś {stawka}$"

    save_data(data)

    await interaction.response.send_message(
        f"{wynik}\nTwoja liczba: {liczba}\nWylosowana: {wylosowana}"
    )

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
