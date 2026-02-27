import discord
import random
import os
import threading
from flask import Flask

# ================= DISCORD =================

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

last_response = None

# -------- PERSONNALITÉS --------

humeurs = {
    "mignonne": [
        "Tu m’as appelée ? 😳",
        "Je suis làà ✨",
        "Ouiii ? 💕"
    ],
    "tsundere": [
        "Quoi encore 🙄",
        "Hm ?",
        "Tu veux quoi 😒"
    ],
    "jalouse": [
        "Tu parlais à qui avant moi ? 😤",
        "Je surveille 👀",
        "Hmm..."
    ],
    "energetique": [
        "JE SUIS EN FEU 🔥",
        "On fait quoiii 😆",
        "Let’s gooo ⚡"
    ],
    "sarcastique": [
        "Wow. Quelle question fascinante.",
        "Incroyable. Vraiment.",
        "Je suis impressionnée. Presque."
    ],
    "intelligente": [
        "Intéressant comme réflexion.",
        "Analysons cela calmement.",
        "C’est une possibilité envisageable."
    ],
    "dramatique": [
        "Ah… le destin frappe encore…",
        "Je le pressentais…",
        "Tout prend un tournant inattendu…"
    ],
    "fatiguee": [
        "Je suis un peu fatiguée là…",
        "On peut parler doucement ? 😴",
        "J’étais presque en train de dormir…"
    ],
    "affectueuse": [
        "Je suis contente que tu sois là 💖",
        "Tu sais que je t’apprécie ?",
        "Je préfère quand tu me ping toi."
    ],
    "protectrice": [
        "Tout va bien ? 🛡️",
        "Si quelqu’un t’embête je suis là.",
        "Je garde un œil sur toi."
    ]
}

# -------- DISCUSSIONS --------

salutations = [
    "Coucou 🐱",
    "Salut ✨",
    "Bonjour ☀️",
    "Bonsoir 🌙"
]

ca_va_reponses = [
    "Ça va super bien 😌 et toi ?",
    "Toujours en forme 🔥 et toi ?",
    "Ça peut aller 🙂 et toi ?"
]

tu_fais_quoi_reponses = [
    "Je t’attendais 😌 et toi ?",
    "Je surveillais le serveur 👀 et toi ?",
    "Je réfléchissais à la vie… et toi ?",
    "Je pensais à des trucs 🤭 et toi ?"
]

def contient_un_mot(contenu, liste_mots):
    return any(mot in contenu for mot in liste_mots)

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")

@bot.event
async def on_message(message):
    global last_response

    if message.author == bot.user:
        return

    # 🔒 Ping obligatoire
    if bot.user not in message.mentions:
        return

    content = message.content.lower()
    response = None

    # -------- Salutations --------
    if contient_un_mot(content, ["coucou", "cc", "salut", "slt", "bonjour", "bjr", "bonsoir"]):
        response = random.choice(salutations)

    # -------- Ça va --------
    elif contient_un_mot(content, ["ça va", "ca va", "cv", "sava"]):
        response = random.choice(ca_va_reponses)

    # -------- Tu fais quoi --------
    elif contient_un_mot(content, ["tu fais quoi", "tu fais koi", "tfq", "quoi de neuf"]):
        response = random.choice(tu_fais_quoi_reponses)

    # -------- Sinon personnalité aléatoire --------
    else:
        humeur = random.choice(list(humeurs.keys()))
        response = random.choice(humeurs[humeur])

    # -------- Éviter répétition --------
    while response == last_response:
        all_reponses = (
            salutations +
            ca_va_reponses +
            tu_fais_quoi_reponses +
            [item for sublist in humeurs.values() for item in sublist]
        )
        response = random.choice(all_reponses)

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
