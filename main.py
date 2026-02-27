import discord
from discord.ext import commands, tasks
import random
import time
import json
import os
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
# MEMOIRE + HUMEUR PERSISTANTE
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
last_response = None

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
        "ping": ["Ouiii ? 🥺", "Je suis là 🫶"],
        "salut": ["Coucou ✨", "Salut toi 🐱"],
        "ca_va": ["Ça va super bien 🥰 et toi ?"],
        "tu_fais_quoi": ["Je pensais à toi 🥺 et toi ?"],
        "default": ["Je suis là si tu veux parler 💕"]
    },
    "energetique": {
        "status": "Énergie max 🔥",
        "ping": ["OUI 🔥", "Je suis prête ⚡"],
        "salut": ["SALUT 🔥"],
        "ca_va": ["Toujours en forme 🔥 et toi ?"],
        "tu_fais_quoi": ["Je cherche un truc fun 😆 et toi ?"],
        "default": ["On fait quoi ? 😏"]
    },
    "affectueuse": {
        "status": "Besoin de câlins 💕",
        "ping": ["Oui toi ? 💕"],
        "salut": ["Coucou toi 💖"],
        "ca_va": ["Ça va mieux quand tu parles 💕 et toi ?"],
        "tu_fais_quoi": ["Je pensais à toi 💭 et toi ?"],
        "default": ["Je suis contente que tu sois là 🫶"]
    },
    "tsundere": {
        "status": "Hm.",
        "ping": ["Quoi encore ?"],
        "salut": ["Salut."],
        "ca_va": ["Ça va. Et toi ?"],
        "tu_fais_quoi": ["Rien… et toi ?"],
        "default": ["Tu veux quoi ?"]
    },
    "protectrice": {
        "status": "Je veille 👀",
        "ping": ["Oui ?"],
        "salut": ["Salut. Je veille."],
        "ca_va": ["Si ça ne va pas je suis là. Et toi ?"],
        "tu_fais_quoi": ["Je surveille le serveur. Et toi ?"],
        "default": ["Je suis là si besoin."]
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
# DETECTION MESSAGE
# ==========================

def detect_type(message):
    msg = message.lower()

    if any(word in msg for word in ["coucou","salut","bonjour","bonsoir"]):
        return "salut"
    if "ça va" in msg or "ca va" in msg:
        return "ca_va"
    if "tu fais quoi" in msg:
        return "tu_fais_quoi"

    return "default"

# ==========================
# EVENTS
# ==========================

@bot.event
async def on_ready():
    print(f"{bot.user} connecté | Humeur: {humeur_actuelle}")
    update_status.start()

@bot.event
async def on_message(message):
    global last_response

    if message.author == bot.user:
        return

    # 🔒 PING OBLIGATOIRE
    if bot.user not in message.mentions:
        return

    update_humeur()

    user_id = str(message.author.id)
    username = message.author.display_name

    if user_id not in memory:
        memory[user_id] = {"name": username, "last": ""}

    mood = humeurs[humeur_actuelle]

    content = message.content.replace(f"<@{bot.user.id}>","").replace(f"<@!{bot.user.id}>","").strip()

    if content == "":
        response = random.choice(mood["ping"])
    else:
        msg_type = detect_type(content)
        response = random.choice(mood.get(msg_type, mood["default"]))

    if response == last_response:
        response = random.choice(mood["default"])

    memory[user_id]["last"] = content
    last_response = response
    save_all()

    await message.channel.send(response)

# ==========================
# AUTO-RESTART EN CAS DE CRASH
# ==========================

while True:
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Crash détecté : {e}")
        time.sleep(5)
