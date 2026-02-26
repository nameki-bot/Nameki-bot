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

# ================= FLASK =================

app = Flask(__name__)

@app.route("/")
def home():
    return "Nameki est en ligne."

# ================= DISCORD =================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

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

@client.event
async def on_ready():
    print(f"Nameki connectée en tant que {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content.lower()
    user = get_user(message.author.id)

    if msg.startswith(PREFIX):

        if msg == "?niveau":
            await message.channel.send(
                f"Relation : {user['relationship']}/100 | Compatibilité : {user['compatibility']}%"
            )
            return

    if client.user not in message.mentions:
        return

    user["relationship"] += random.randint(1, 2)
    user["relationship"] = min(100, user["relationship"])
    save_memory()

    await message.channel.send(random.choice([
        "Je t’écoute.",
        "Hmm.",
        "Intéressant.",
        "Continue."
    ]))

# ================= THREAD BOT =================

def run_bot():
    client.run(TOKEN)

threading.Thread(target=run_bot).start()

# ================= LANCE FLASK (PRINCIPAL) =================

port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
