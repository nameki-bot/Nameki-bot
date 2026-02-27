import discord
import random
import os
import threading
import time
from flask import Flask

# ================= DISCORD =================

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

last_response = None

# -------- PERSONNALITÉS --------

humeurs = {
    "mignonne": {
        "default": ["Ouiii ? 💕", "Je suis làà ✨", "Tu m’as appelée ? 😳"],
        "ca_va": ["Ça va super bien 😌 et toi ?"],
        "tu_fais_quoi": ["Je t’attendais 😌 et toi ?"]
    },
    "tsundere": {
        "default": ["Quoi encore 🙄", "Hm ?", "Tu veux quoi 😒"],
        "ca_va": ["Ça va. Voilà. et toi ?"],
        "tu_fais_quoi": ["Rien qui te regarde… et toi ?"]
    },
    "protectrice": {
        "default": ["Je veille 👀", "Tout va bien ? 🛡️"],
        "ca_va": ["Si ça va pas je suis là. Et toi ?"],
        "tu_fais_quoi": ["Je surveille le serveur. Et toi ?"]
    },
    "energetique": {
        "default": ["ON BOUGE 🔥", "Let’s gooo ⚡"],
        "ca_va": ["Toujours en forme 🔥 et toi ?"],
        "tu_fais_quoi": ["Je cherche de l’action 😆 et toi ?"]
    },
    "affectueuse": {
        "default": ["Je suis contente que tu sois là 💖"],
        "ca_va": ["Ça va encore mieux quand tu parles 😌 et toi ?"],
        "tu_fais_quoi": ["Je pensais un peu à toi… et toi ?"]
    }
}

# -------- Humeur stable 10 min --------

humeur_actuelle = random.choice(list(humeurs.keys()))
dernier_changement = time.time()
DUREE_HUMEUR = 600  # 10 minutes

def update_humeur():
    global humeur_actuelle, dernier_changement
    if time.time() - dernier_changement > DUREE_HUMEUR:
        humeur_actuelle = random.choice(list(humeurs.keys()))
        dernier_changement = time.time()

def contient(contenu, mots):
    return any(mot in contenu for mot in mots)

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")

@bot.event
async def on_message(message):
    global last_response

    if message.author == bot.user:
        return

    if bot.user not in message.mentions:
        return

    update_humeur()
    content = message.content.lower()

    mood = humeurs[humeur_actuelle]

    if contient(content, ["coucou", "cc", "salut", "bonjour", "bonsoir"]):
        response = random.choice(["Coucou 🐱", "Salut ✨", "Bonjour ☀️", "Bonsoir 🌙"])

    elif contient(content, ["ça va", "ca va", "cv", "sava"]):
        response = random.choice(mood["ca_va"])

    elif contient(content, ["tu fais quoi", "tfq", "quoi de neuf"]):
        response = random.choice(mood["tu_fais_quoi"])

    else:
        response = random.choice(mood["default"])

    if response == last_response:
        response = random.choice(mood["default"])

    last_response = response
    await message.channel.send(response)

# ================= FLASK KEEP ALIVE =================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive"

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    thread = threading.Thread(target=run)
    thread.start()

keep_alive()

# ================= RUN =================

bot.run(os.environ["TOKEN"])
