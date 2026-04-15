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
            "warns": 0,
            "exp": 0,
            "level": 1,
            "bank": 0,
"last_interest": 0,
            "cases": 0,
"inventory": []
        }
        save_data(data)
    return data

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    data = get_user(message.author.id)
    user_id = str(message.author.id)

    # dodaj EXP
    exp_gain = random.randint(5, 15)
    data[user_id]["exp"] += exp_gain

    # sprawdź level up
    level = data[user_id]["level"]
    exp = data[user_id]["exp"]

    if exp >= level * 100:
        data[user_id]["level"] += 1
        data[user_id]["exp"] = 0

        await message.channel.send(
            f"🎉 {message.author.mention} wbił level {level + 1}!"
        )

    save_data(data)

    await bot.process_commands(message)  # ważne!

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


@bot.tree.command(name="ruletka", description="Zagraj w ruletkę")
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

VIP_ROLE_ID = 1493505575932395592  # <- TU WSTAW ID ROLI

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

@bot.tree.command(name="level", description="Sprawdź swój level 📊")
async def level(interaction: discord.Interaction, user: discord.Member = None):

    if user is None:
        user = interaction.user

    data = get_user(user.id)
    user_id = str(user.id)

    lvl = data[user_id]["level"]
    exp = data[user_id]["exp"]

    await interaction.response.send_message(
        f"📊 {user.mention}\nLevel: {lvl}\nEXP: {exp}/{lvl*100}"
    )

@bot.tree.command(name="toplvl", description="Top leveli 🏆")
async def top(interaction: discord.Interaction):

    data = load_data()

    sorted_users = sorted(
        data.items(),
        key=lambda x: x[1].get("level", 0),
        reverse=True
    )

    msg = "🏆 TOP LEVELI:\n"

    for i, (user_id, info) in enumerate(sorted_users[:10], start=1):
        msg += f"{i}. <@{user_id}> - lvl {info.get('level', 0)}\n"

    await interaction.response.send_message(msg)

@bot.tree.command(name="allin", description="All-in 💀 50/50")
async def allin(interaction: discord.Interaction):

    data = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    kasa = data[user_id]["money"]

    if kasa <= 0:
        await interaction.response.send_message("❌ Nie masz kasy", ephemeral=True)
        return

    import random
    win = random.choice([True, False])

    if win:
        data[user_id]["money"] *= 2
        msg = f"💰 WYGRANA! Masz teraz {data[user_id]['money']}$"
    else:
        data[user_id]["money"] = 0
        msg = "💀 PRZEGRANA! Straciłeś wszystko..."

    save_data(data)

    await interaction.response.send_message(msg)

@bot.tree.command(name="sloty", description="Automaty 🎰")
async def sloty(interaction: discord.Interaction, kwota: int):

    data = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    if kwota <= 0 or data[user_id]["money"] < kwota:
        await interaction.response.send_message("❌ Zła kwota", ephemeral=True)
        return

    import random
    symbole = ["🍒", "🍋", "🍉", "💎"]

    wynik = [random.choice(symbole) for _ in range(3)]

    msg = " | ".join(wynik) + "\n"

    if wynik[0] == wynik[1] == wynik[2]:
        wygrana = kwota * 5
        data[user_id]["money"] += wygrana
        msg += f"💰 JACKPOT! +{wygrana}$"
    elif wynik[0] == wynik[1] or wynik[1] == wynik[2]:
        wygrana = kwota * 2
        data[user_id]["money"] += wygrana
        msg += f"💰 Wygrana! +{wygrana}$"
    else:
        data[user_id]["money"] -= kwota
        msg += f"💸 Przegrana -{kwota}$"

    save_data(data)

    await interaction.response.send_message(msg)

@bot.tree.command(name="jackpot", description="Sprawdź jackpot 🏆")
async def jackpot_cmd(interaction: discord.Interaction):
    global jackpot
    await interaction.response.send_message(f"🏆 Jackpot wynosi: {jackpot}$")

@bot.tree.command(name="buycase", description="Kup skrzynkę 🎁")
async def buycase(interaction: discord.Interaction):

    data = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    cena = 100

    if data[user_id]["money"] < cena:
        await interaction.response.send_message("❌ Nie masz kasy", ephemeral=True)
        return

    data[user_id]["money"] -= cena
    data[user_id]["cases"] += 1

    save_data(data)

    await interaction.response.send_message("🎁 Kupiłeś skrzynkę!")

@bot.tree.command(name="opencase", description="Otwórz skrzynkę 🎰")
async def opencase(interaction: discord.Interaction):

    data = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    if data[user_id]["cases"] <= 0:
        await interaction.response.send_message("❌ Nie masz skrzynek", ephemeral=True)
        return

    data[user_id]["cases"] -= 1

    # 🎲 losowanie rarity
    rarity = random.choices(
        ["common", "rare", "epic", "legendary", "knife"],
        weights=[50, 30, 15, 4, 1]
    )[0]

    skiny = {
        "common": ["P250 Sand Dune", "Glock-18 Groundwater"],
        "rare": ["AK-47 Elite Build", "M4A1-S Decimator"],
        "epic": ["AWP Neo-Noir", "AK-47 Neon Rider"],
        "legendary": ["M4A4 Howl", "AK-47 Fire Serpent"],
        "knife": ["Karambit Doppler", "Butterfly Fade"]
    }

    item = random.choice(skiny[rarity])

    # 💰 wartość
    values = {
        "common": 20,
        "rare": 80,
        "epic": 200,
        "legendary": 1000,
        "knife": 5000
    }

    value = values[rarity]

    data[user_id]["inventory"].append({
        "name": item,
        "rarity": rarity,
        "value": value
    })

    save_data(data)

    await interaction.response.send_message(
        f"🎰 Otworzyłeś skrzynkę!\n"
        f"🎁 {item}\n"
        f"💎 Rzadkość: {rarity}\n"
        f"💰 Wartość: {value}$"
    )

@bot.tree.command(name="deposit", description="Wpłać kasę do banku 🏦")
async def deposit(interaction: discord.Interaction, kwota: int):

    data = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    if kwota <= 0 or data[user_id]["money"] < kwota:
        await interaction.response.send_message("❌ Zła kwota", ephemeral=True)
        return

    data[user_id]["money"] -= kwota
    data[user_id]["bank"] += kwota

    save_data(data)

    await interaction.response.send_message(
        f"🏦 Wpłaciłeś {kwota}$ do banku!"
    )

@bot.tree.command(name="withdraw", description="Wypłać kasę z banku 💸")
async def withdraw(interaction: discord.Interaction, kwota: int):

    data = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    if kwota <= 0 or data[user_id]["bank"] < kwota:
        await interaction.response.send_message("❌ Zła kwota", ephemeral=True)
        return

    data[user_id]["bank"] -= kwota
    data[user_id]["money"] += kwota

    save_data(data)

    await interaction.response.send_message(
        f"💸 Wypłaciłeś {kwota}$ z banku!"
    )

@bot.tree.command(name="interest", description="Odbierz odsetki 💰")
async def interest(interaction: discord.Interaction):

    data = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    now = time.time()

    # ⏳ cooldown 1h
    if now - data[user_id].get("last_interest", 0) < 3600:
        await interaction.response.send_message("⏳ Poczekaj 1h", ephemeral=True)
        return

    bank = data[user_id]["bank"]

    if bank <= 0:
        await interaction.response.send_message("❌ Nie masz nic w banku", ephemeral=True)
        return

    # 💰 2% odsetek
    profit = int(bank * 0.02)

    data[user_id]["bank"] += profit
    data[user_id]["last_interest"] = now

    save_data(data)

    await interaction.response.send_message(
        f"💰 Otrzymałeś {profit}$ odsetek!"
    )

@bot.tree.command(name="inventory", description="Twój ekwipunek 🎒")
async def inventory(interaction: discord.Interaction):

    data = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    inv = data[user_id]["inventory"]

    if not inv:
        await interaction.response.send_message("❌ Pusty ekwipunek")
        return

    msg = "🎒 Twój ekwipunek:\n"

    for i, item in enumerate(inv, start=1):
        msg += f"{i}. {item['name']} ({item['rarity']}) - {item['value']}$\n"

    await interaction.response.send_message(msg)

@bot.tree.command(name="sell", description="Sprzedaj item 💸")
async def sell(interaction: discord.Interaction, index: int):

    data = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    inv = data[user_id]["inventory"]

    if index <= 0 or index > len(inv):
        await interaction.response.send_message("❌ Zły numer", ephemeral=True)
        return

    item = inv.pop(index - 1)

    data[user_id]["money"] += item["value"]

    save_data(data)

    await interaction.response.send_message(
        f"💰 Sprzedałeś {item['name']} za {item['value']}$"
    )

@bot.tree.command(name="stats", description="Statystyki serwera 📊")
async def stats(interaction: discord.Interaction):

    guild = interaction.guild

    users = len([m for m in guild.members if not m.bot])
    bots = len([m for m in guild.members if m.bot])
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)

    embed = discord.Embed(
        title="📊 Statystyki serwera",
        color=discord.Color.blue()
    )

    embed.add_field(name="👥 Użytkownicy", value=users)
    embed.add_field(name="🤖 Boty", value=bots)
    embed.add_field(name="💬 Tekstowe", value=text_channels)
    embed.add_field(name="🔊 Głosowe", value=voice_channels)

    await interaction.response.send_message(embed=embed)

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

from datetime import timedelta

@bot.tree.command(name="mute", description="Wycisz użytkownika 🔇")
async def mute(interaction: discord.Interaction, user: discord.Member):

    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ Brak permisji", ephemeral=True)
        return

    try:
        await user.timeout(timedelta(hours=6))
        await interaction.response.send_message(f"🔇 {user.mention} wyciszony na 6h")
    except Exception as e:
        await interaction.response.send_message(f"❌ Błąd: {e}", ephemeral=True)

from datetime import timedelta

@bot.tree.command(name="unmute", description="Odcisz użytkownika 🔊")
async def unmute(interaction: discord.Interaction, user: discord.Member):

    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ Brak permisji", ephemeral=True)
        return

    try:
        # usuwa timeout
        await user.timeout(None)

        await interaction.response.send_message(
            f"🔊 {user.mention} został odciszony!"
        )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ Błąd: {e}",
            ephemeral=True
        )

bot.tree.command(name="unban", description="Odbanuj użytkownika 🔓")
async def unban(interaction: discord.Interaction, user_id: str):

    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ Brak permisji", ephemeral=True)
        return

    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)

        await interaction.response.send_message(
            f"🔓 {user} został odbanowany!"
        )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ Błąd: {e}",
            ephemeral=True
        )

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
