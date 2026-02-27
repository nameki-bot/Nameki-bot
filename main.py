import discord
from discord.ext import commands, tasks
import random
import time
import json
import os
import asyncio
from flask import Flask
from threading import Thread

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================
# SERVEUR WEB (ANTI-SLEEP)
# ==========================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

def run_web():
    app.run(host="0.0.0.0", port=10000)

Thread(target=run_web).start()

# ==========================
# MEMOIRE PERSISTANTE
# ==========================

MEMORY_FILE = "memory.json"

if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
else:
    data = {
        "users": {},
        "humeur": random.choice(["mignonne","energetique","affectueuse","tsundere","protectrice"]),
        "last_change": time.time()
    }

memory = data["users"]
humeur_actuelle = data["humeur"]
dernier_changement = data["last_change"]
last_response_time = {}

def save_all():
    with open(MEMORY_FILE, "w") as f:
        json.dump({
            "users": memory,
            "humeur": humeur_actuelle,
            "last_change": dernier_changement
        }, f)

# ==========================
# HUMEURS
# ==========================

humeurs = {
    "mignonne": {
        "status": "Mode mignonne 🥺",
        "base": ["Ouiii ? 💕", "Tu m’as appelée ?", "Je suis là pour toi 💗"]
    },
    "energetique": {
        "status": "Énergie max 🔥",
        "base": ["OUI 🔥", "Toujours prête ⚡", "On fait quoi ?"]
    },
    "affectueuse": {
        "status": "Besoin de câlins 💕",
        "base": ["Je suis là 🤍", "Tu avais besoin de moi ?", "Je t’écoute."]
    },
    "tsundere": {
        "status": "Hm.",
        "base": ["Quoi encore.", "Hm ?", "Tu veux quoi ?"]
    },
    "protectrice": {
        "status": "Je veille 👀",
        "base": ["Oui ?", "Je suis là si besoin.", "Tout va bien ?"]
    }
}

# ==========================
# CHANGEMENT HUMEUR 2H
# ==========================

def update_humeur():
    global humeur_actuelle, dernier_changement

    if time.time() - dernier_changement > 7200:
        humeur_actuelle = random.choice(list(humeurs.keys()))
        dernier_changement = time.time()
        save_all()

# ==========================
# STATUS DYNAMIQUE
# ==========================

@tasks.loop(minutes=5)
async def update_status():
    await bot.change_presence(
        activity=discord.Game(name=humeurs[humeur_actuelle]["status"])
    )

# ==========================
# DETECTION INSULTE
# ==========================

def detect_insulte(message):
    insultes = ["nulle","idiote","tg","tais toi","folle","ferme","stupide"]
    msg = message.lower()
    return any(word in msg for word in insultes)

# ==========================
# REPONSE HUMAINE
# ==========================

async def repondre(message, user_data):

    # réflexion humaine
    base_delay = random.uniform(2.0, 4.0)
    extra_delay = min(len(message.content) * 0.04, 2)
    total_delay = base_delay + extra_delay

    async with message.channel.typing():
        await asyncio.sleep(total_delay)

    base = random.choice(humeurs[humeur_actuelle]["base"])
    affinite = user_data["affinite"]
    emotion = user_data["emotion"]

    # Variation selon affinité
    if affinite < 20:
        reponse = "..."
    elif affinite < 40:
        reponse = base.replace("💕","").replace("💗","").replace("🤍","")
    elif affinite > 80:
        reponse = base + " 🥰"
    else:
        reponse = base

    # Si insulte récente → froide
    if emotion == "froide":
        reponse = "Hm. " + reponse

    # Hésitation réaliste
    if random.random() < 0.25:
        msg = await message.channel.send("...")
        await asyncio.sleep(random.uniform(1.0,1.8))
        await msg.edit(content=reponse)
    else:
        await message.channel.send(reponse)

# ==========================
# EVENTS
# ==========================

@bot.event
async def on_ready():
    print(f"{bot.user} connecté | Humeur: {humeur_actuelle}")
    update_status.start()

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    # PING OBLIGATOIRE
    if bot.user not in message.mentions:
        return

    update_humeur()

    user_id = str(message.author.id)
    username = message.author.display_name

    if user_id not in memory:
        memory[user_id] = {
            "name": username,
            "last": "",
            "affinite": 50,
            "emotion": "neutre"
        }

    user_data = memory[user_id]

    content = message.content.replace(f"<@{bot.user.id}>","").replace(f"<@!{bot.user.id}>","").strip()

    # Anti spam 5 sec
    now = time.time()
    if user_id in last_response_time:
        if now - last_response_time[user_id] < 5:
            return
    last_response_time[user_id] = now

    # Gestion émotionnelle
    if detect_insulte(content):
        user_data["affinite"] -= 15
        user_data["emotion"] = "froide"
    else:
        user_data["affinite"] += 2
        user_data["emotion"] = "gentille"

    user_data["affinite"] = max(0, min(100, user_data["affinite"]))

    await repondre(message, user_data)

    save_all()

# ==========================
# AUTO RESTART
# ==========================

while True:
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Crash détecté : {e}")
        time.sleep(5)
