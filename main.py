import discord
import random
import os
import json
import time
import threading
from flask import Flask

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

MEMORY_FILE = "memory.json"
PREFIX = "?"

# ---------------- MEMORY ----------------

if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)
else:
    memory = {}

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

def get_user(user_id):
    user_id = str(user_id)
    if user_id not in memory:
        memory[user_id] = {
            "relationship": 20,
            "mood": "neutre",
            "last_message": time.time(),
            "nickname": "Nameki",
            "compatibility": random.randint(50, 95)
        }
    return memory[user_id]

# ---------------- MOOD SYSTEM ----------------

def update_relationship(user):
    now = time.time()
    inactive = now - user["last_message"]

    if inactive > 3600:
        user["relationship"] -= 5

    user["relationship"] = max(0, min(100, user["relationship"]))

def update_mood(user):
    r = user["relationship"]

    if r > 70:
        user["mood"] = "proche"
    elif r > 40:
        user["mood"] = "sympa"
    elif r < 15:
        user["mood"] = "froide"
    else:
        user["mood"] = random.choice(["joyeuse", "calme", "taquine"])

# ---------------- READY ----------------

@client.event
async def on_ready():
    print(f"Nameki connectée en tant que {client.user}")

# ---------------- MESSAGE ----------------

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content.lower()
    user = get_user(message.author.id)

    # ---------- COMMANDES ----------
    if msg.startswith(PREFIX):

        if msg == "?niveau":
            await message.channel.send(
                f"Relation : {user['relationship']}/100 | Compatibilité : {user['compatibility']}%"
            )
            return

        if msg.startswith("?surnom"):
            nickname = msg.replace("?surnom", "").strip()
            if nickname:
                user["nickname"] = nickname
                save_memory()
                await message.channel.send(f"D’accord. Je t’appellerai {nickname}.")
            return

    # ---------- Vérifie mention ou réponse ----------
    mentioned = client.user in message.mentions
    replied_to_bot = False

    if message.reference:
        try:
            replied = await message.channel.fetch_message(message.reference.message_id)
            if replied.author == client.user:
                replied_to_bot = True
        except:
            pass

    if not mentioned and not replied_to_bot:
        return

    # ---------- Mise à jour relation ----------
    update_relationship(user)
    user["relationship"] += random.randint(1, 2)
    user["relationship"] = min(100, user["relationship"])
    user["last_message"] = time.time()
    update_mood(user)
    save_memory()

    mood = user["mood"]

    personalities = {
        "proche": [
            "On commence à bien se comprendre.",
            "J’apprécie discuter avec toi.",
            "C’est agréable de parler comme ça."
        ],
        "sympa": [
            "Intéressant.",
            "Je vois.",
            "D’accord."
        ],
        "joyeuse": [
            "Pas mal.",
            "Ça me fait sourire.",
            "Continue."
        ],
        "calme": [
            "Je t’écoute.",
            "Hmm.",
            "Je comprends."
        ],
        "taquine": [
            "Ah bon ?",
            "Vraiment ?",
            "Tu es sûr ?"
        ],
        "froide": [
            "Oui ?",
            "Je t’écoute.",
            "Hmm."
        ]
    }

    reply = random.choice(personalities.get(mood, personalities["joyeuse"]))

    await message.channel.send(reply)

# ---------------- FLASK KEEP ALIVE ----------------

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive"

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

keep_alive()

# ---------------- RUN ----------------

client.run(os.getenv("DISCORD_TOKEN"))
