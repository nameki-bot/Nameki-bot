import discord
from discord.ext import commands
import random
import os
import json
from flask import Flask
from threading import Thread
from datetime import datetime

# ========== FLASK ==========
app = Flask('')

@app.route('/')
def home():
    return "Nameki est en ligne 🐱💕"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    Thread(target=run).start()

# ========== DISCORD ==========
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents)

DATA_FILE = "nameki_memory.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        memory = json.load(f)
else:
    memory = {}

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(memory, f, indent=4)

def get_user(user_id):
    user_id = str(user_id)
    if user_id not in memory:
        memory[user_id] = {
            "affection": 10,
            "personality": random.choice(["douce", "énergique", "sarcastique", "mystérieuse"]),
            "name": None
        }
    return memory[user_id]

def daily_mood():
    moods = ["adorable", "taquine", "calme", "énergique"]
    today = datetime.now().strftime("%Y-%m-%d")
    random.seed(today)
    return random.choice(moods)

@bot.event
async def on_ready():
    print(f"{bot.user} connecté 🌸")

@bot.command()
async def affection(ctx):
    user = get_user(ctx.author.id)
    await ctx.send(f"Ton affection est à {user['affection']} 💕")

@bot.command()
async def personnalite(ctx, style):
    user = get_user(ctx.author.id)
    styles = ["douce", "énergique", "sarcastique", "mystérieuse"]
    if style.lower() in styles:
        user["personality"] = style.lower()
        save()
        await ctx.send(f"Ma personnalité est maintenant {style} 😌")
    else:
        await ctx.send("Choisis : douce / énergique / sarcastique / mystérieuse")

@bot.command()
async def prenom(ctx, *, name):
    user = get_user(ctx.author.id)
    user["name"] = name
    save()
    await ctx.send(f"D'accord… je t’appellerai {name} maintenant 🥺")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user = get_user(message.author.id)
    content = message.content.lower()

    if bot.user.mentioned_in(message):

        user["affection"] += random.randint(1, 3)
        user["affection"] = min(user["affection"], 100)
        save()

        affection = user["affection"]
        personality = user["personality"]
        name = user["name"] if user["name"] else message.author.display_name
        mood = daily_mood()

        # Mode protectrice
        if any(insult in content for insult in ["idiot", "nul", "stupide"]):
            await message.channel.send(f"Hé ! 😠 Ne parle pas comme ça à {name} !")
            return

        # Salutations
        if any(word in content for word in ["coucou", "salut", "bonjour"]):
            await message.channel.send(f"Coucou {name} 🐱💕")
            return

        # Ça va
        if "ça va" in content or "ca va" in content:
            if affection > 50:
                await message.channel.send(f"Je vais super bien maintenant que tu es là {name} 🥺💕")
            else:
                await message.channel.send("Ça va tranquille 😌 Et toi ?")
            return

        # Triste
        if "triste" in content:
            await message.channel.send(f"Viens là {name}… je suis avec toi 🥺💕")
            return

        # Réponse selon humeur quotidienne
        if mood == "adorable":
            responses = ["Tu es mignon aujourd’hui 🥺", "J’aime bien discuter avec toi 💕"]
        elif mood == "taquine":
            responses = ["Hmm… intéressant 😏", "Tu racontes toujours ça toi."]
        elif mood == "calme":
            responses = ["Je t’écoute.", "Continue."]
        else:
            responses = ["Je suis pleine d’énergie aujourd’hui 🔥", "On fait quoi {name} ? 😆"]

        await message.channel.send(random.choice(responses))

    await bot.process_commands(message)

# ========== LANCEMENT ==========
keep_alive()
bot.run(os.environ["TOKEN"])
