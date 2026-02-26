import discord
import random
import os
import json
import time
import threading
from flask import Flask

# ================= CONFIG =================

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "?"
MEMORY_FILE = "memory.json"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

# ================= FLASK (OBLIGATOIRE POUR RENDER FREE) =================

app = Flask(__name__)

@app.route("/")
def home():
    return "Nameki est en ligne."

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

# ================= MEMORY =================

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
            "last_message": time.time(),
            "compatibility": random.randint(50, 95)
        }
    return memory[user_id]

# ================= READY =================

@client.event
async def on_ready():
    print(f"Nameki connectée en tant que {client.user}")

# ================= MESSAGE =================

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
                await message.channel.send(f"D’accord. Je t’appellerai {nickname}.")
            return

    # ---------- Répond SEULEMENT si ping ----------
    if client.user not in message.mentions:
        return

    user["relationship"] += random.randint(1, 2)
    user["relationship"] = min(100, user["relationship"])
    user["last_message"] = time.time()
    save_memory()

    responses = [
        "Je t’écoute.",
        "Hmm.",
        "Intéressant.",
        "Continue.",
        "Je vois."
    ]

    await message.channel.send(random.choice(responses))

# ================= RUN =================

client.run(TOKEN)
