import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import asyncio
import json
import time

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
        data[str(user_id)] = {
            "money": 100,
            "last_work": 0,
            "last_daily": 0,
            "warns": 0
        }
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
    user = str(interaction.user.id)

    now = time.time()

    if now - data[user]["last_work"] < 60:  # 60 sekund cooldown
        await interaction.response.send_message("⏳ Poczekaj chwilę!", ephemeral=True)
        return

    zarobek = random.randint(20, 80)
    data[user]["money"] += zarobek
    data[user]["last_work"] = now

    save_data(data)

    await interaction.response.send_message(f"💼 Zarobiłeś {zarobek}$!")
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

@bot.tree.command(name="daily", description="Codzienna nagroda 🎁")
async def daily(interaction: discord.Interaction):
    data = get_user(interaction.user.id)
    user = str(interaction.user.id)

    now = time.time()

    if now - data[user]["last_daily"] < 86400:
        await interaction.response.send_message("❌ Już odebrałeś daily!", ephemeral=True)
        return

    nagroda = random.randint(100, 300)
    data[user]["money"] += nagroda
    data[user]["last_daily"] = now

    save_data(data)

    await interaction.response.send_message(f"🎁 Dostałeś {nagroda}$!")

@bot.tree.command(name="top", description="Najbogatsi gracze 💰")
async def top(interaction: discord.Interaction):
    data = load_data()

    ranking = sorted(data.items(), key=lambda x: x[1]["money"], reverse=True)

    msg = "🏆 TOP 5:\n"

    for i, (user_id, info) in enumerate(ranking[:5], start=1):
        user = await bot.fetch_user(int(user_id))
        msg += f"{i}. {user.name} - {info['money']}$\n"

    await interaction.response.send_message(msg)

@bot.tree.command(name="pay", description="Wyślij komuś kasę 💸")
async def pay(interaction: discord.Interaction, user: discord.Member, kwota: int):
    data = get_user(interaction.user.id)
    sender = str(interaction.user.id)
    receiver = str(user.id)

    if kwota <= 0:
        await interaction.response.send_message("❌ Podaj poprawną kwotę", ephemeral=True)
        return

    if data[sender]["money"] < kwota:
        await interaction.response.send_message("❌ Nie masz tyle kasy", ephemeral=True)
        return

    data = get_user(user.id)

    data[sender]["money"] -= kwota
    data[receiver]["money"] += kwota

    save_data(data)

    await interaction.response.send_message(
        f"💸 Przelałeś {kwota}$ do {user.mention}"
    )

@bot.tree.command(name="shop", description="Sklep 🛒")
async def shop(interaction: discord.Interaction):
    msg = (
        "🛒 **SKLEP**\n\n"
        "1️⃣ VIP - 1000$\n"
        "Nadaje specjalną rangę 😎"
    )

    await interaction.response.send_message(msg)

VIP_ROLE_ID = 11493505575932395592  # <- TU WSTAW ID ROLI

@bot.tree.command(name="buy", description="Kup coś ze sklepu 💸")
async def buy(interaction: discord.Interaction, item: str):
    data = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    if item.lower() == "vip":

        if data[user_id]["money"] < 1000:
            await interaction.response.send_message("❌ Nie masz 1000$", ephemeral=True)
            return

        role = interaction.guild.get_role(VIP_ROLE_ID)

        if role in interaction.user.roles:
            await interaction.response.send_message("❌ Masz już VIP", ephemeral=True)
            return

        # zabieramy kasę
        data[user_id]["money"] -= 1000
        save_data(data)

        # nadajemy rolę
        await interaction.user.add_roles(role)

        await interaction.response.send_message("🎉 Kupiłeś rangę VIP!")

    else:
        await interaction.response.send_message("❌ Nie ma takiego itemu", ephemeral=True)

# ===== MODERACJA =====

from datetime import timedelta

@bot.tree.command(name="warn", description="Daj ostrzeżenie ⚠️")
async def warn(interaction: discord.Interaction, user: discord.Member, powod: str):

    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ Nie masz permisji", ephemeral=True)
        return

    data = get_user(user.id)
    user_id = str(user.id)

    data[user_id]["warns"] += 1
    warns = data[user_id]["warns"]

    save_data(data)

    msg = f"⚠️ {user.mention} dostał warna!\nPowód: {powod}\nWarny: {warns}"

    # 🔥 SYSTEM KAR
    try:
        if warns == 1:
            await user.timeout(timedelta(hours=6))
            msg += "\n🔇 Kara: mute na 6 godzin"

        elif warns == 2:
            await user.kick(reason="2 warny")
            msg += "\n👢 Kara: wyrzucony z serwera"

        elif warns >= 3:
            await user.ban(reason="3 warny")
            msg += "\n🔨 Kara: BAN"

    except Exception as e:
        msg += f"\n❌ Błąd przy karze: {e}"

    await interaction.response.send_message(msg)
@bot.tree.command(name="warns", description="Sprawdź warny 📋")
async def warns(interaction: discord.Interaction, user: discord.Member):
    data = get_user(user.id)
    user_id = str(user.id)

    warns = data[user_id]["warns"]

    await interaction.response.send_message(
        f"📋 {user.mention} ma {warns} warnów"
    )

@bot.tree.command(name="clearwarns", description="Usuń warny 🧹")
async def clearwarns(interaction: discord.Interaction, user: discord.Member):

    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ Nie masz permisji", ephemeral=True)
        return

    data = get_user(user.id)
    user_id = str(user.id)

    data[user_id]["warns"] = 0
    save_data(data)

    await interaction.response.send_message(
        f"🧹 Wyczyszczono warny dla {user.mention}"
    )

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
