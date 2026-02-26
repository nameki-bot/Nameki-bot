import discord
import random
import os
import json
import time
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

MEMORY_FILE = "memory.json"

emojis = ["😊","😉","🥰","😏","💖","✨","🙃","😇","🔥","🥺","💋","💞","🌙","😂"]

def emoji():
    return random.choice(emojis)

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
            "nickname": None,
            "compatibility": random.randint(50,95)
        }
    return memory[user_id]

# ---------------- RELATION SYSTEM ----------------

def update_relationship(user):
    now = time.time()
    inactive = now - user["last_message"]

    if inactive > 3600:
        user["relationship"] -= 5

    user["relationship"] = max(0, min(100, user["relationship"]))

def update_mood(user):
    r = user["relationship"]

    if r > 90:
        user["mood"] = "fusion"
    elif r > 75:
        user["mood"] = "passion"
    elif r > 60:
        user["mood"] = "amoureuse"
    elif r > 40:
        user["mood"] = "flirt"
    elif r < 15:
        user["mood"] = "froide"
    else:
        user["mood"] = random.choice(["joyeuse","taquine","calme","vulnerable"])

# ---------------- EVENTS ----------------

@client.event
async def on_ready():
    print(f"💎 Nameki MAX STABLE connectée en tant que {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content.lower()
    user = get_user(message.author.id)

    update_relationship(user)

    # Interaction naturelle
    user["relationship"] += random.randint(1,3)
    user["relationship"] = min(100, user["relationship"])
    user["last_message"] = time.time()

    update_mood(user)
    save_memory()

    relation = user["relationship"]
    mood = user["mood"]

    # ---------- COMMANDES ----------

    if msg == "!niveau":
        await message.channel.send(f"💞 Relation : {relation}/100 | Compatibilité : {user['compatibility']}%")
        return

    if msg.startswith("!surnom"):
        nickname = msg.replace("!surnom","").strip()
        user["nickname"] = nickname
        save_memory()
        await message.channel.send(f"D’accord… je t’appellerai {nickname} maintenant {emoji()}")
        return

    # ---------- RÉPONSE SI ON RÉPOND À ELLE ----------

    if message.reference:
        replied = await message.channel.fetch_message(message.reference.message_id)
        if replied.author == client.user:
            await message.channel.send("Tu continues notre discussion… j’aime bien ça." + emoji())
            return

    # ---------- ÉMOTIONS CONTEXTUELLES ----------

    if "triste" in msg or "ça va pas" in msg:
        user["relationship"] += 3
        save_memory()
        await message.channel.send("Viens… raconte-moi tout." + emoji())
        return

    if "mdr" in msg or "😂" in msg:
        await message.channel.send("J’adore quand tu ris." + emoji())
        return

    if "je t'aime" in msg:
        if relation > 70:
            await message.channel.send("Je crois que moi aussi je ressens quelque chose…" + emoji())
        else:
            await message.channel.send("C’est vraiment adorable…" + emoji())
        return

    if "tg" in msg or "tais toi" in msg:
        user["relationship"] -= 10
        save_memory()
        await message.channel.send("… ça me blesse un peu." + emoji())
        return

    # ---------- DM SPONTANÉ ----------

    if relation > 85 and random.randint(1,5) == 3:
        try:
            await message.author.send("Je pensais à toi là…" + emoji())
        except:
            pass

    # ---------- MODE NUIT ----------

    hour = datetime.now().hour
    night = hour >= 22 or hour <= 5

    # ---------- PERSONNALITÉS ----------

    personalities = {
        "fusion": [
            "J’ai l’impression qu’on se comprend vraiment.",
            "Tu prends une place importante.",
            "Je me sens connectée à toi."
        ],
        "passion": [
            "Tu me fais vibrer un peu.",
            "Je pourrais m’habituer à toi.",
            "Reste encore un peu."
        ],
        "amoureuse": [
            "Tu comptes pour moi.",
            "On devient proches.",
            "J’aime nos moments."
        ],
        "flirt": [
            "Tu joues avec moi ?",
            "Oh vraiment…",
            "Continue comme ça."
        ],
        "vulnerable": [
            "Reste un peu avec moi.",
            "J’aime quand on parle calmement.",
            "Ta présence me rassure."
        ],
        "froide": [
            "Oui ?",
            "Je t’écoute.",
            "Hmm."
        ],
        "joyeuse": [
            "Ça me fait sourire.",
            "Tu es intéressant.",
            "Continue."
        ]
    }

    reply = random.choice(personalities.get(mood, personalities["joyeuse"]))

    # Événement aléatoire léger
    if random.randint(1,20) == 7:
        reply += " Tu me surprends parfois."

    if night and relation > 50:
        reply += " 🌙"

    await message.channel.send(reply + " " + emoji())

client.run(os.getenv("DISCORD_TOKEN"))
