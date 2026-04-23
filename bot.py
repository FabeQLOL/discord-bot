import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import asyncio
import json
import time
import string

ALLOWED_GUILD_ID = 1492852181303431289

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

premium_users = set()


# ===== READY =====
OWNER_ID = 1490030330084720892 # <- tutaj wstaw swoje ID Discord

@bot.event
async def on_member_join(member: discord.Member):
    owner = await bot.fetch_user(OWNER_ID)

    try:
        await owner.send(
            f"📢 Nowy użytkownik wszedł na serwer!\n\n"
            f"👤 Nick: {member.name}\n"
            f"🆔 ID: {member.id}\n"
            f"📅 Konto utworzone: {member.created_at.strftime('%Y-%m-%d')}"
        )
    except:
        print("Nie mogę wysłać DM do właściciela.")

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")

    try:
        bot.tree.clear_commands()  # 🔥 usuwa duplikaty
        synced = await bot.tree.sync()
        print(f"Zsynchronizowano {len(synced)} komend 😎")
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
    uid = str(user_id)

    if uid not in data:
        data[uid] = {
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

    return data, uid

def load_balance():
    with open("balance.json", "r") as f:
        return json.load(f)

def save_balance(data):
    with open("balance.json", "w") as f:
        json.dump(data, f)

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
@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Komendy zsynchronizowane")

@bot.tree.interaction_check
async def global_check(interaction:discord.Interaction):
    return True

BAD_WORDS = ["fuck off", "Moron", "fuck", "shit", "idiot", "fucking", "fuckin", "the shit", "faggot", "cunt", "scum", "penis", "dick", "dih", "motherfuck", "motherfucker", "cum"]

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if any(word in message.content.lower() for word in BAD_WORDS):
    await message.delete()
    await message.channel.send(
        f"⚠️ {message.author.mention} Watch your language!",
        delete_after=5
    )

    if "http" in message.content:
    if not message.author.guild_permissions.manage_messages:
        await message.delete()
        await message.channel.send(
            f"🚫 {message.author.mention} No links allowed!",
            delete_after=5
        )

data, _ = get_user(message.author.id)
user_id = str(message.author.id)

data[user_id]["warns"] += 1
warns = data[user_id]["warns"]

save_data(data)

if warns == 3:
    await message.author.timeout(discord.timedelta(minutes=10))
    await message.channel.send(f"⏳ {message.author.mention} muted for 10 min.")

elif warns == 5:
    await message.author.kick(reason="Too many warns")

log_channel = discord.utils.get(message.guild.text_channels, name="logs")

if log_channel:
    await log_channel.send(
        f"📋 {message.author} got a warn ({warns}) for: {message.content}"
    )

# ===== KOMENDY =====

# -------------------------
# LANGUAGE SYSTEM
# -------------------------

def load_lang():
    try:
        with open("lang.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_lang(data):
    with open("lang.json", "w") as f:
        json.dump(data, f, indent=4)

langs = load_lang()

def get_lang(user_id):
    return langs.get(str(user_id), "pl")

# -------------------------
# TEXTS (TRANSLATIONS)
# -------------------------
texts = {
    "allin": {
        "pl": "💸 Wchodzisz all-in!",
        "en": "💸 Going all-in!"
    },
    "balance": {
        "pl": "💰 Twoje saldo: {coins}",
        "en": "💰 Your balance: {coins}"
    },
    "ban": {
        "pl": "🔨 Użytkownik został zbanowany",
        "en": "🔨 User has been banned"
    },
    "buy": {
        "pl": "🛒 Kupiono przedmiot",
        "en": "🛒 Item purchased"
    },
    "buycase": {
        "pl": "📦 Kupiono skrzynkę",
        "en": "📦 Case purchased"
    },
    "clearwarns": {
        "pl": "🧹 Wyczyściliśmy warny",
        "en": "🧹 Warnings cleared"
    },
    "coinflip": {
        "pl": "🪙 Rzut monetą: {result}",
        "en": "🪙 Coinflip result: {result}"
    },
    "daily": {
        "pl": "💰 Otrzymałeś {coins} coins!",
        "en": "💰 You received {coins} coins!"
    },
    "deposit": {
        "pl": "🏦 Wpłaciłeś {coins} coins",
        "en": "🏦 Deposited {coins} coins"
    },
    "hej": {
        "pl": "👋 Hej!",
        "en": "👋 Hello!"
    },
    "interest": {
        "pl": "📈 Otrzymałeś odsetki: {coins}",
        "en": "📈 You earned interest: {coins}"
    },
    "inventory": {
        "pl": "🎒 Twój ekwipunek",
        "en": "🎒 Your inventory"
    },
    "jackpot": {
        "pl": "🎰 Jackpot!",
        "en": "🎰 Jackpot!"
    },
    "kick": {
        "pl": "👢 Użytkownik został wyrzucony",
        "en": "👢 User has been kicked"
    },
    "level": {
        "pl": "📊 Twój poziom: {level}",
        "en": "📊 Your level: {level}"
    },
    "losuj": {
        "pl": "🎲 Wylosowano: {number}",
        "en": "🎲 You rolled: {number}"
    },
    "mute": {
        "pl": "🔇 Użytkownik został wyciszony",
        "en": "🔇 User has been muted"
    },
    "opencase": {
        "pl": "📦 Otwierasz skrzynkę...",
        "en": "📦 Opening case..."
    },
    "pay": {
        "pl": "💸 Wysłałeś {coins} coins",
        "en": "💸 You sent {coins} coins"
    },
    "ruletka": {
        "pl": "🎡 Kręcisz ruletką...",
        "en": "🎡 Spinning roulette..."
    },
    "sell": {
        "pl": "💵 Sprzedano przedmiot",
        "en": "💵 Item sold"
    },
    "shop": {
        "pl": "🛍️ Sklep",
        "en": "🛍️ Shop"
    },
    "sloty": {
        "pl": "🎰 Kręcisz slotami...",
        "en": "🎰 Spinning slots..."
    },
    "stats": {
        "pl": "📊 Twoje statystyki",
        "en": "📊 Your stats"
    },
    "top": {
        "pl": "🏆 Ranking graczy",
        "en": "🏆 Leaderboard"
    },
    "toplvl": {
        "pl": "🏅 Ranking poziomów",
        "en": "🏅 Level leaderboard"
    },
    "unban": {
        "pl": "🔓 Użytkownik odbanowany",
        "en": "🔓 User unbanned"
    },
    "unmute": {
        "pl": "🔊 Użytkownik odciszony",
        "en": "🔊 User unmuted"
    },
    "warn": {
        "pl": "⚠️ Użytkownik otrzymał warna",
        "en": "⚠️ User warned"
    },
    "warns": {
        "pl": "⚠️ Lista warnów",
        "en": "⚠️ Warnings list"
    },
    "withdraw": {
        "pl": "🏧 Wypłaciłeś {coins} coins",
        "en": "🏧 Withdrew {coins} coins"
    },
    "avatar": {
        "pl": "🖼️ Avatar użytkownika",
        "en": "🖼️ User avatar"
    },
    "8ball": {
        "pl": "🎱 Odpowiedź: {answer}",
        "en": "🎱 Answer: {answer}"
    },
    "userinfo": {
        "pl": "👤 Informacje o użytkowniku",
        "en": "👤 User info"
 }
}
def t(key, lang="pl", **kwargs):
    return texts[key][lang].format(**kwargs)

    
@bot.tree.command(name="pl", description="Ustaw język polski")
async def set_pl(interaction: discord.Interaction):
    langs[str(interaction.user.id)] = "pl"
    save_lang(langs)
    await interaction.response.send_message("🇵🇱 Ustawiono język polski!")

@bot.tree.command(name="en", description="Set English language")
async def set_en(interaction: discord.Interaction):
    langs[str(interaction.user.id)] = "en"
    save_lang(langs)
    await interaction.response.send_message("🇬🇧 Language set to English!")


@bot.tree.command(name="hello", description="Say hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("👋 Hello!")

@bot.tree.command(name="work", description="Earn Money 💼")
async def work(interaction: discord.Interaction):
    data, user_id = get_user(interaction.user.id)

    now = time.time()

    # ⏳ cooldown 10 minut (600 sekund)
    if now - data[user_id]["last_work"] < 600:
        await interaction.response.send_message(
            "⏳ You can work every 10 minutes!",
            ephemeral=True
        )
        return

    zarobek = random.randint(20, 80)

    data[user_id]["money"] += zarobek
    data[user_id]["last_work"] = now

    save_data(data)

    await interaction.response.send_message(
        f"💼 You worked and earned. **{zarobek}$** 💰"
    )

@bot.tree.command(name="balance", description="Account Balance")
async def balance(interaction: discord.Interaction):
    data, user_id = get_user(interaction.user.id)

    await interaction.response.send_message(
        str(data[user_id]["money"]) + "$"
    )

@bot.tree.command(name="daily", description="Daily reward")
async def daily(interaction: discord.Interaction):
    coins = random.randint(50, 150)
    await interaction.response.send_message(f"💰 You got {coins} coins!")

@bot.tree.command(name="deposit", description="Deposit money into the bank. 🏦")
async def deposit(interaction: discord.Interaction, amount: int):

    data, user_id = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    if amount <= 0 or data[user_id]["money"] < amount:
        await interaction.response.send_message("❌ Incorrect amount", ephemeral=True)
        return

    data[user_id]["money"] -= amount
    data[user_id]["bank"] += amount

    save_data(data)

    await interaction.response.send_message(
        f"🏦 You deposited {amount}$ into the bank.!"
    )
@bot.tree.command(name="withdraw", description="Withdraw cash from the bank. 💸")
async def withdraw(interaction: discord.Interaction, amount: int):

    data, user_id = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    if amount <= 0 or data[user_id]["bank"] < amount:
        await interaction.response.send_message("❌ Incorrect Amount", ephemeral=True)
        return

    data[user_id]["bank"] -= amount
    data[user_id]["money"] += amount

    save_data(data)

    await interaction.response.send_message(
        f"💸 You withdrew {amount}$ from the bank.!"
    )

@bot.tree.command(name="pay", description="Send Money 💸")
async def pay(interaction: discord.Interaction, user: discord.Member, amount: int):

    data, _ = get_user(interaction.user.id)
    sender = str(interaction.user.id)
    receiver = str(user.id)

    if amount <= 0:
        await interaction.response.send_message("❌ Invalid amount.", ephemeral=True)
        return

    if data[sender]["money"] < amount:
        await interaction.response.send_message("❌ Not enough money.", ephemeral=True)
        return

    # UPEWNIJ SIĘ że receiver istnieje
    if receiver not in data:
        data[receiver] = {"money": 0, "warns": 0}

    data[sender]["money"] -= amount
    data[receiver]["money"] += amount

    save_data(data)

    await interaction.response.send_message(
        f"💸 You sent {amount}$ to {user.mention}"
    )

@bot.tree.command(name="interest", description="Collect Interest 💰")
async def interest(interaction: discord.Interaction):

    data, user_id = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    now = time.time()

    # ⏳ cooldown 1h
    if now - data[user_id].get("last_interest", 0) < 3600:
        await interaction.response.send_message("⏳ Wait 1h", ephemeral=True)
        return

    bank = data[user_id]["bank"]

    if bank <= 0:
        await interaction.response.send_message("❌ You have nothing in the bank.", ephemeral=True)
        return

    # 💰 2% odsetek
    profit = int(bank * 0.02)

    data[user_id]["bank"] += profit
    data[user_id]["last_interest"] = now

    save_data(data)

    await interaction.response.send_message(
        f"💰 You have received {profit}$ Interest!"
    )
# -------------------------
# SHOP / ITEMS
# -------------------------


@bot.tree.command(name="sell", description="Sell ​​Item 💸")
async def sell(interaction: discord.Interaction, index: int):
    data, user_id = get_user(interaction.user.id)

    inv = data[user_id]["inventory"]

    if not inv:
        await interaction.response.send_message("❌ Your inventory is empty.", ephemeral=True)
        return

    if index <= 0 or index > len(inv):
        await interaction.response.send_message("❌ Invalid item number", ephemeral=True)
        return

    item = inv.pop(index - 1)

    data[user_id]["money"] += item["value"]

    save_data(data)

    await interaction.response.send_message(
        f"💰 You sold **{item['name']}** for **{item['value']}$**"
    )
@bot.tree.command(name="inventory", description="Your Inventory 🎒")
async def inventory(interaction: discord.Interaction):
    data, user_id = get_user(interaction.user.id)

    inv = data[user_id]["inventory"]

    if not inv:
        await interaction.response.send_message("❌ Your inventory is empty.")
        return

    msg = "🎒 **Your Inventory:**\n\n"

    for i, item in enumerate(inv, start=1):
        msg += f"{i}. {item['name']} ({item['rarity']}) - {item['value']}$\n"

    await interaction.response.send_message(msg)

@bot.tree.command(name="buycase", description="Buy a case 🎁")
async def buycase(interaction: discord.Interaction):

    data, user_id = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    cena = 100

    if data[user_id]["money"] < cena:
        await interaction.response.send_message("❌ You don't have any money.", ephemeral=True)
        return

    data[user_id]["money"] -= cena
    data[user_id]["cases"] += 1

    save_data(data)

    await interaction.response.send_message("🎁 You bought a case!")
    
@bot.tree.command(name="opencase", description="Open Case 🎰")
async def opencase(interaction: discord.Interaction):

    data, user_id = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    if data[user_id]["cases"] <= 0:
        await interaction.response.send_message("❌ You don't have any case's", ephemeral=True)
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
        f"🎰 You opened the case!\n"
        f"🎁 {item}\n"
        f"💎 Rarity: {rarity}\n"
        f"💰 Value: {value}$"
    )
# -------------------------
# GAMBLING
# -------------------------

@bot.tree.command(name="coinflip", description="Flip a coin")
async def coinflip(interaction: discord.Interaction):
    result = random.choice(["Heads 🦅", "Tails 🪙"])
    await interaction.response.send_message(result)

@bot.tree.command(name="slots", description="Slot Machines 🎰")
async def sloty(interaction: discord.Interaction, amount: int):

    data, user_id = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    if amount <= 0 or data[user_id]["money"] < amount:
        await interaction.response.send_message("❌ Incorrect amount", ephemeral=True)
        return

    import random
    symbole = ["🍒", "🍋", "🍉", "💎"]

    wynik = [random.choice(symbole) for _ in range(3)]

    msg = " | ".join(wynik) + "\n"

    if wynik[0] == wynik[1] == wynik[2]:
        wygrana = amount * 5
        data[user_id]["money"] += wygrana
        msg += f"💰 JACKPOT! +{wygrana}$"
    elif wynik[0] == wynik[1] or wynik[1] == wynik[2]:
        wygrana = amount * 2
        data[user_id]["money"] += wygrana
        msg += f"💰 Win! +{wygrana}$"
    else:
        data[user_id]["money"] -= amount
        msg += f"💸 Defeat -{amount}$"

    save_data(data)

    await interaction.response.send_message(msg)

@bot.tree.command(name="roulette", description="Play roulette")
async def ruletka(interaction: discord.Interaction, number: int, bet: int):

    if number < 1 or number > 36:
        await interaction.response.send_message("Number 1–36 ❌", ephemeral=True)
        return

    data, user_id = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    if data[user_id]["money"] < bet:
        await interaction.response.send_message("You don't have that much money. ❌", ephemeral=True)
        return

    wylosowana = random.randint(1, 36)

    if number == wylosowana:
        wygrana = bet * 10
        data[user_id]["money"] += wygrana
        wynik = f"🎉 YOU WON {wygrana}$!"
    else:
        data[user_id]["money"] -= bet
        wynik = f"😢 You lost {bet}$"

    save_data(data)

    await interaction.response.send_message(
        f"{wynik}\nYour Number: {number}\nRandomly Selected: {wylosowana}"
    )

@bot.tree.command(name="allin", description="All-in 💀 50/50")
async def allin(interaction: discord.Interaction):

    data, _ = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    kasa = data[user_id]["money"]

    if kasa <= 0:
        await interaction.response.send_message("❌ You don't have any money.", ephemeral=True)
        return

    import random
    win = random.choice([True, False])

    if win:
        data[user_id]["money"] *= 2
        msg = f"💰 WIN! You now have {data[user_id]['money']}$"
    else:
        data[user_id]["money"] = 0
        msg = "💀 DEFEAT! You've lost everything..."

    save_data(data)

    await interaction.response.send_message(msg)
    
@bot.tree.command(name="jackpot", description="Play the jackpot 🎰")
async def jackpot(interaction: discord.Interaction, amount: int):

    await interaction.response.defer()

    try:
        data = load_balance()
        user_id = str(interaction.user.id)

        if user_id not in data:
            data[user_id] = 1000

        if amount <= 0:
            await interaction.followup.send("❌ Incorrect amount!")
            return

        if data[user_id] < amount:
            await interaction.followup.send("❌ You don't have any money.!")
            return

        data[user_id] -= amount

        import random
        roll = random.randint(1, 100)

        if roll <= 50:
            wynik = f"💀 You lose {amount}$"
        else:
            win = amount * 2
            data[user_id] += win
            wynik = f"🤑 You win {win}$"

        save_balance(data)

        await interaction.followup.send(
            f"🎰 {wynik}\n💰 You now have {data[user_id]}$"
        )

    except Exception as e:
        await interaction.followup.send(f"❌ Błąd: {e}")

# -------------------------
# LEVEL / STATS
# -------------------------

@bot.tree.command(name="level", description="Check your level 📊")
async def level(interaction: discord.Interaction, user: discord.Member = None):

    if user is None:
        user = interaction.user

    data, user_id = get_user(interaction.user.id)
    user_id = str(user.id)

    lvl = data[user_id]["level"]
    exp = data[user_id]["exp"]

    await interaction.response.send_message(
        f"📊 {user.mention}\nLevel: {lvl}\nEXP: {exp}/{lvl*100}"
    )

@bot.tree.command(name="stats", description="Server Stats 📊")
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

    embed.add_field(name="👥 Users", value=users)
    embed.add_field(name="🤖 Bots", value=bots)
    embed.add_field(name="💬 Text Channels", value=text_channels)
    embed.add_field(name="🔊 Voice Channels", value=voice_channels)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="leaderboards", description="Top Players 🏆")
async def top(interaction: discord.Interaction):

    data = load_data()

    sorted_users = sorted(
        data.items(),
        key=lambda x: x[1].get("level", 0),
        reverse=True
    )

    msg = "🏆 TOP PLAYERS:\n"

    for i, (user_id, info) in enumerate(sorted_users[:10], start=1):
        msg += f"{i}. <@{user_id}> - lvl {info.get('level', 0)}\n"

    await interaction.response.send_message(msg)

@bot.tree.command(name="top", description="The Richest Players 💰")
async def top(interaction: discord.Interaction):
    data = load_data()

    ranking = sorted(data.items(), key=lambda x: x[1]["money"], reverse=True)

    msg = "🏆 TOP 5:\n"

    for i, (user_id, info) in enumerate(ranking[:5], start=1):
        user = await bot.fetch_user(int(user_id))
        msg += f"{i}. {user.name} - {info['money']}$\n"

    await interaction.response.send_message(msg)

# -------------------------
# FUN
# -------------------------

@bot.tree.command(name="roll", description="Roll number")
async def roll(interaction: discord.Interaction):
    number = random.randint(1, 100)
    await interaction.response.send_message(f"🎲 {number}")

@bot.tree.command(name="8ball", description="Magic ball")
@app_commands.describe(question="Your question")
async def eightball(interaction: discord.Interaction, question: str):
    answer = random.choice(["Yes", "No", "Maybe"])
    await interaction.response.send_message(f"🎱 {answer}")

@bot.tree.command(name="avatar", description="Get avatar")
@app_commands.describe(user="User")
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    if user is None:
        user = interaction.user
    await interaction.response.send_message(user.avatar.url)

@bot.tree.command(name="userinfo", description="User info")
@app_commands.describe(user="User")
async def userinfo(interaction: discord.Interaction, user: discord.Member = None):
    if user is None:
        user = interaction.user
    await interaction.response.send_message(f"👤 {user.name} | ID: {user.id}")

# -------------------------
# ADMIN (basic)
# -------------------------

@bot.tree.command(name="ban", description="Ban the user.")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason"):
    await user.ban(reason=reason)
    await interaction.response.send_message(f"🔨 Banned {user} | Reason: {reason}")

@bot.tree.command(name="unban", description="Unban User 🔓")
async def unban(interaction: discord.Interaction, user_id: str):

    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ No permission", ephemeral=True)
        return

    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)

        await interaction.response.send_message(
            f"🔓 {user} was unbanned.!"
        )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ Błąd: {e}",
            ephemeral=True
        )

@bot.tree.command(name="kick", description="Kick User")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason"):
    await user.kick(reason=reason)
    await interaction.response.send_message(f"👢 Kicked {user} | Reason: {reason}")

from datetime import timedelta

@bot.tree.command(name="mute", description="Mute User 🔇")
async def mute(interaction: discord.Interaction, user: discord.Member):

    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ No permission", ephemeral=True)
        return

    try:
        await user.timeout(timedelta(hours=6))
        await interaction.response.send_message(f"🔇 {user.mention} Muted for 6 hours")
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

from datetime import timedelta

@bot.tree.command(name="unmute", description="Unmute User 🔊")
async def unmute(interaction: discord.Interaction, user: discord.Member):

    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ No permission", ephemeral=True)
        return

    try:
        # usuwa timeout
        await user.timeout(None)

        await interaction.response.send_message(
            f"🔊 {user.mention} was unmuted.!"
        )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ Error: {e}",
            ephemeral=True
        )


@bot.tree.command(name="warn", description="Issue a warning. ⚠️")
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str):

    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ No permission", ephemeral=True)
        return

    data, _ = get_user(interaction.user.id)
    target_id = str(user.id)

    if target_id not in data:
        data[target_id] = {"money": 0, "warns": 0}

    data[target_id]["warns"] += 1
    warns = data[target_id]["warns"]

    save_data(data)

    await interaction.response.send_message(
        f"⚠️ {user.mention} got warned!\nReason: {reason}\nWarns: {warns}"
    )
@bot.tree.command(name="warnings", description="Check warns 📋")
async def warnings(interaction: discord.Interaction, user: discord.Member):

    data, _ = get_user(interaction.user.id)
    user_id = str(user.id)

    if user_id not in data:
        data[user_id] = {"money": 0, "warns": 0}

    warns = data[user_id]["warns"]

    await interaction.response.send_message(
        f"📋 {user.mention} has {warns} warns"
    )
@bot.tree.command(name="clearwarns", description="Delete warns 🧹")
async def clearwarns(interaction: discord.Interaction, user: discord.Member):

    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ No permission", ephemeral=True)
        return

    data, _ = get_user(interaction.user.id)
    target_id = str(user.id)

    if target_id not in data:
        data[target_id] = {"money": 0, "warns": 0}

    data[target_id]["warns"] = 0
    save_data(data)

    await interaction.response.send_message(
        f"🧹 Warnings cleared for {user.mention}"
    )

@bot.tree.command(name="hejpl", description="Powitanie")
async def hej(interaction: discord.Interaction):
    await interaction.response.send_message("Siema 😎")

@bot.tree.command(name="losujpl", description="Losuje liczbę 1-100")
async def losuj(interaction: discord.Interaction):
    await interaction.response.send_message(str(random.randint(1, 100)))

@bot.tree.command(name="coinflippl", description="Orzeł czy reszka")
async def coinflip(interaction: discord.Interaction):
    wynik = random.choice(["Orzeł 🦅", "Reszka 🪙"])
    await interaction.response.send_message(wynik)

@bot.tree.command(name="balancepl", description="Stan konta")
async def balance(interaction: discord.Interaction):
    data, user_id = get_user(interaction.user.id)

    await interaction.response.send_message(
        str(data[user_id]["money"]) + "$"
    )

@bot.tree.command(name="workpl", description="Zarabiaj pieniądze 💼")
async def work(interaction: discord.Interaction):
    data, user_id = get_user(interaction.user.id)

    now = time.time()

    # ⏳ cooldown 10 minut (600 sekund)
    if now - data[user_id]["last_work"] < 600:
        await interaction.response.send_message(
            "⏳ Możesz pracować co 10 minut!",
            ephemeral=True
        )
        return

    zarobek = random.randint(20, 80)

    data[user_id]["money"] += zarobek
    data[user_id]["last_work"] = now

    save_data(data)

    await interaction.response.send_message(
        f"💼 Pracowałeś i zarobiłeś **{zarobek}$** 💰"
    )

@bot.tree.command(name="ruletkapl", description="Zagraj w ruletkę")
async def ruletka(interaction: discord.Interaction, liczba: int, bet: int):

    if liczba < 1 or liczba > 36:
        await interaction.response.send_message("Liczba 1-36 ❌", ephemeral=True)
        return

    data, user_id = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    if data[user_id]["money"] < bet:
        await interaction.response.send_message("Nie masz tyle kasy ❌", ephemeral=True)
        return

    wylosowana = random.randint(1, 36)

    if liczba == wylosowana:
        wygrana = bet * 10
        data[user_id]["money"] += wygrana
        wynik = f"🎉 WYGRAŁEŚ {wygrana}$!"
    else:
        data[user_id]["money"] -= bet
        wynik = f"😢 Przegrałeś {bet}$"

    save_data(data)

    await interaction.response.send_message(
        f"{wynik}\nTwoja liczba: {liczba}\nWylosowana: {wylosowana}"
    )

@bot.tree.command(name="dailypl", description="Codzienna nagroda 🎁")
async def daily(interaction: discord.Interaction):
    data, user_id = get_user(interaction.user.id)
    user = str(interaction.user.id)

    now = time.time()

    if now - data[user_id]["last_daily"] < 86400:
        await interaction.response.send_message("❌ Już odebrałeś daily!", ephemeral=True)
        return

    nagroda = random.randint(100, 300)
    data[user]["money"] += nagroda
    data[user]["last_daily"] = now

    save_data(data)

    await interaction.response.send_message(f"🎁 Dostałeś {nagroda}$!")

@bot.tree.command(name="toppl", description="Najbogatsi gracze 💰")
async def top(interaction: discord.Interaction):
    data = load_data()

    ranking = sorted(data.items(), key=lambda x: x[1]["money"], reverse=True)

    msg = "🏆 TOP 5:\n"

    for i, (user_id, info) in enumerate(ranking[:5], start=1):
        user = await bot.fetch_user(int(user_id))
        msg += f"{i}. {user.name} - {info['money']}$\n"

    await interaction.response.send_message(msg)

@bot.tree.command(name="paypl", description="Wyślij komuś kasę 💸")
async def pay(interaction: discord.Interaction, user: discord.Member, kwota: int):
    data, user_id = get_user(interaction.user.id)
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


@bot.tree.command(name="levelpl", description="Sprawdź swój level 📊")
async def level(interaction: discord.Interaction, user: discord.Member = None):

    if user is None:
        user = interaction.user

    data, user_id = get_user(interaction.user.id)
    user_id = str(user.id)

    lvl = data[user_id]["level"]
    exp = data[user_id]["exp"]

    await interaction.response.send_message(
        f"📊 {user.mention}\nLevel: {lvl}\nEXP: {exp}/{lvl*100}"
    )

@bot.tree.command(name="toplvlpl", description="Top leveli 🏆")
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

@bot.tree.command(name="allinpl", description="All-in 💀 50/50")
async def allin(interaction: discord.Interaction):

    data, user_id = get_user(interaction.user.id)
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

@bot.tree.command(name="slotypl", description="Automaty 🎰")
async def sloty(interaction: discord.Interaction, kwota: int):

    data, user_id = get_user(interaction.user.id)
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

@bot.tree.command(name="buycasepl", description="Kup skrzynkę 🎁")
async def buycase(interaction: discord.Interaction):

    data, user_id = get_user(interaction.user.id)
    user_id = str(interaction.user.id)

    cena = 100

    if data[user_id]["money"] < cena:
        await interaction.response.send_message("❌ Nie masz kasy", ephemeral=True)
        return

    data[user_id]["money"] -= cena
    data[user_id]["cases"] += 1

    save_data(data)

    await interaction.response.send_message("🎁 Kupiłeś skrzynkę!")

@bot.tree.command(name="opencasepl", description="Otwórz skrzynkę 🎰")
async def opencase(interaction: discord.Interaction):

    data, user_id = get_user(interaction.user.id)
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

@bot.tree.command(name="depositppl", description="Wpłać kasę do banku 🏦")
async def deposit(interaction: discord.Interaction, kwota: int):

    data, user_id = get_user(interaction.user.id)
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

@bot.tree.command(name="withdrawpl", description="Wypłać kasę z banku 💸")
async def withdraw(interaction: discord.Interaction, kwota: int):

    data, user_id = get_user(interaction.user.id)
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

@bot.tree.command(name="interestpl", description="Odbierz odsetki 💰")
async def interest(interaction: discord.Interaction):

    data, user_id = get_user(interaction.user.id)
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

@bot.tree.command(name="inventorypl", description="Twój ekwipunek 🎒")
async def inventory(interaction: discord.Interaction):
    data, user_id = get_user(interaction.user.id)

    inv = data[user_id]["inventory"]

    if not inv:
        await interaction.response.send_message("❌ Twój ekwipunek jest pusty")
        return

    msg = "🎒 **Twój ekwipunek:**\n\n"

    for i, item in enumerate(inv, start=1):
        msg += f"{i}. {item['name']} ({item['rarity']}) - {item['value']}$\n"

    await interaction.response.send_message(msg)
    
@bot.tree.command(name="sellpl", description="Sprzedaj item 💸")
async def sell(interaction: discord.Interaction, index: int):
    data, user_id = get_user(interaction.user.id)

    inv = data[user_id]["inventory"]

    if not inv:
        await interaction.response.send_message("❌ Twój ekwipunek jest pusty", ephemeral=True)
        return

    if index <= 0 or index > len(inv):
        await interaction.response.send_message("❌ Zły numer itemu", ephemeral=True)
        return

    item = inv.pop(index - 1)

    data[user_id]["money"] += item["value"]

    save_data(data)

    await interaction.response.send_message(
        f"💰 Sprzedałeś **{item['name']}** za **{item['value']}$**"
    )

@bot.tree.command(name="statspl", description="Statystyki serwera 📊")
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

@bot.tree.command(name="jackpotpl", description="Zagraj w jackpot 🎰")
async def jackpot(interaction: discord.Interaction, amount: int):

    await interaction.response.defer()

    try:
        data = load_balance()
        user_id = str(interaction.user.id)

        if user_id not in data:
            data[user_id] = 1000

        if amount <= 0:
            await interaction.followup.send("❌ Zła kwota!")
            return

        if data[user_id] < amount:
            await interaction.followup.send("❌ Nie masz kasy!")
            return

        data[user_id] -= amount

        import random
        roll = random.randint(1, 100)

        if roll <= 50:
            wynik = f"💀 Przegrałeś {amount}$"
        else:
            win = amount * 2
            data[user_id] += win
            wynik = f"🤑 Wygrałeś {win}$"

        save_balance(data)

        await interaction.followup.send(
            f"🎰 {wynik}\n💰 Masz teraz {data[user_id]}$"
        )

    except Exception as e:
        await interaction.followup.send(f"❌ Błąd: {e}")
        
# ===== MODERACJA =====

from datetime import timedelta

@bot.tree.command(name="warnpl", description="Daj ostrzeżenie ⚠️")
async def warn(interaction: discord.Interaction, user: discord.Member, powod: str):

    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ Nie masz permisji", ephemeral=True)
        return

    data, user_id = get_user(interaction.user.id)
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

@bot.tree.command(name="clearwarnspl", description="Usuń warny 🧹")
async def clearwarns(interaction: discord.Interaction, user: discord.Member):

    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ Nie masz permisji", ephemeral=True)
        return

    data, user_id = get_user(interaction.user.id)
    user_id = str(user.id)

    data[user_id]["warns"] = 0
    save_data(data)

    await interaction.response.send_message(
        f"🧹 Wyczyszczono warny dla {user.mention}"
    )

@bot.tree.command(name="banpl", description="Banuje użytkownika")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "Brak powodu"):
    await user.ban(reason=reason)
    await interaction.response.send_message(f"🔨 Zbanowano {user} | Powód: {reason}")

@bot.tree.command(name="kickpl", description="Wyrzuca użytkownika")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "Brak powodu"):
    await user.kick(reason=reason)
    await interaction.response.send_message(f"👢 Wyrzucono {user} | Powód: {reason}")

from datetime import timedelta

@bot.tree.command(name="mutepl", description="Wycisz użytkownika 🔇")
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

@bot.tree.command(name="unmutepl", description="Odcisz użytkownika 🔊")
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

@bot.tree.command(name="unbanpl", description="Odbanuj użytkownika 🔓")
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

@bot.tree.command(name="8ballpl", description="Magiczna kula")
@app_commands.describe(question="Twoje pytanie")
async def eightball(interaction: discord.Interaction, question: str):
    responses = [
        "Tak 👍",
        "Nie ❌",
        "Możliwe 🤔",
        "Raczej tak 😏",
        "Raczej nie 😬",
        "Zapytaj później ⏳"
    ]
    await interaction.response.send_message(f"🎱 {random.choice(responses)}")

@bot.tree.command(name="userinfopl", description="Informacje o użytkowniku")
@app_commands.describe(user="Wybierz użytkownika")
async def userinfo(interaction: discord.Interaction, user: discord.Member = None):
    if user is None:
        user = interaction.user

    await interaction.response.send_message(f"""
👤 **User info**
Nick: {user.name}
ID: {user.id}
Dołączył: {user.joined_at}
""")

@bot.tree.command(name="avatarpl", description="Pokaż avatar")
@app_commands.describe(user="Wybierz użytkownika")
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    if user is None:
        user = interaction.user
    await interaction.response.send_message(user.avatar.url)


# ===== BŁĘDY (np. brak permisji) =====

@ban.error
@kick.error
@mute.error
async def mod_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("❌ You don't have permission!", ephemeral=True)
    else:
        await interaction.response.send_message("❌ An error occurred.", ephemeral=True)

@bot.tree.interaction_check
async def global_check(interaction: discord.Interaction):

    # Jeśli ktoś używa bota w DM
    if interaction.guild is None:
        await interaction.response.send_message(
            "Nie możesz używać FabBota poza serwerem!",
            ephemeral=True
        )
        return False

    # Jeśli ktoś jest na innym serwerze
    if interaction.guild.id != ALLOWED_GUILD_ID:
        await interaction.response.send_message(
            "You dont have permission to use FabBot,\n Contact fabeqgg for more info",
            ephemeral=True
        )
        return False

    return True
    
# ===== TOKEN =====

token = os.getenv("TOKEN_DISCORD")

if not token:
    print("❌ ERROR: Token not found!")
else:
    bot.run(token)
