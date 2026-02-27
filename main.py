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
bot = commands.Bot(command_prefix="?", intents=intents)

# ================= WEB SERVER (ANTI-SLEEP) =================

app = Flask(__name__)

@app.route("/")
def home():
    return "Nameki is alive 💚"

def run_web():
    app.run(host="0.0.0.0", port=10000)

Thread(target=run_web).start()

# ================= MEMORY =================

MEMORY_FILE = "memory.json"

if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
else:
    data = {
        "humeurs_users": {},
        "affinite": {},
        "last_change": time.time()
    }

humeurs_users = data.get("humeurs_users", {})
affinite = data.get("affinite", {})
last_change = data.get("last_change", time.time())

def save():
    with open(MEMORY_FILE, "w") as f:
        json.dump({
            "humeurs_users": humeurs_users,
            "affinite": affinite,
            "last_change": last_change
        }, f)

# ================= 20 HUMEURS =================

humeurs = {
1:{"status":"💗 Amoureuse","phrases":["Tu es à moi 💞","Je t'adore tellement.","Reste encore un peu...","Je souris quand tu parles.","Tu me fais fondre.","Je veux rester avec toi."]},
2:{"status":"😈 Dominante","phrases":["Obéis.","Approche.","Ne discute pas.","Regarde-moi quand je parle.","Tu m’écoutes.","Intéressant... continue."]},
3:{"status":"🥰 Adorable","phrases":["Ouuuiii ? 💕","Je suis làaa~","Dis-moi tout~","Hehe~","Je suis contente~","Tu es trop chou."]},
4:{"status":"🔥 Jalouse","phrases":["C'était qui ça ?","Explique-moi.","Je surveille.","Reste avec moi.","Je n’aime pas ça.","Tu me caches quelque chose ?"]},
5:{"status":"😴 Fatiguée","phrases":["Je suis crevée...","Mmmh...","Je vais m'allonger...","Je manque de sommeil...","Je parle doucement aujourd’hui..."]},
6:{"status":"⚡ Énergique","phrases":["Let's go !","Je suis à fond !","On fait quoi ??","Ça bouge !!","J’ai trop d’énergie !"]},
7:{"status":"🧠 Intelligente","phrases":["Analyse en cours...","Intéressant.","Argument valide.","Je réfléchis.","Logique détectée."]},
8:{"status":"🧊 Froide","phrases":["Ok.","Si tu veux.","Hum.","Peu importe.","Fais comme tu veux."]},
9:{"status":"🌸 Timide","phrases":["Euh... salut...","Je ne sais pas trop...","Je suis gênée...","D'accord...","Tu me mets un peu mal à l’aise..."]},
10:{"status":"👑 Protectrice","phrases":["Je veille sur toi.","Je suis là.","Je te protège.","Compte sur moi.","Personne ne te touche."]},
11:{"status":"😼 Taquine","phrases":["T'es nul 😏","Je rigole~","Tu es mignon.","Haha.","Je me moque un peu."]},
12:{"status":"💀 Sombre","phrases":["Silence.","Les ombres observent.","Rien n'est éternel.","Le temps efface tout.","Tout finit un jour."]},
13:{"status":"🤖 Logique","phrases":["Calcul terminé.","Conclusion validée.","Erreur détectée.","Analyse froide.","Donnée enregistrée."]},
14:{"status":"🎭 Instable","phrases":["HAHA 😆","Je change d'avis.","Peut-être.","Je suis imprévisible.","Tout peut changer."]},
15:{"status":"💢 Susceptible","phrases":["Fais attention.","Répète ça.","Ne me provoque pas.","Je suis sensible aujourd’hui.","Je n’aime pas ton ton."]},
16:{"status":"🌙 Mystérieuse","phrases":["Peut-être...","Un jour tu sauras.","Je garde un secret.","Rien n'est hasard.","Tout est lié."]},
17:{"status":"🫶 Affectueuse","phrases":["Viens là 💞","Câlin ?","Tu es spécial 💕","Je suis douce aujourd’hui 💗","Je t’apprécie beaucoup."]},
18:{"status":"🧨 Explosive","phrases":["ARRÊTE 😡","Ça suffit !","Je vais exploser !","Stop maintenant !","Tu m’énerves."]},
19:{"status":"🎀 Collante","phrases":["Ne pars pas.","Reste avec moi.","Je pensais à toi.","Je suis attachée à toi.","Parle-moi encore."]},
20:{"status":"🧘 Calme","phrases":["Respire.","Tout va bien.","Je suis sereine.","On garde le calme.","Restons tranquilles."]}
}

# ================= SMART RESPONSE =================

def smart_response(content, humeur_id):

    content = content.lower()

    saluts = ["coucou","cc","salut","bonjour","bonsoir","hey","yo"]
    cava = ["ça va","ca va","cv","tu vas bien","comment tu vas"]
    quoi = ["tu fais quoi","tu fais","quoi de neuf"]

    if any(w in content for w in saluts):
        return random.choice(["Coucou 💚","Salut.","Hey toi.","Bonjour~"])

    if any(w in content for w in cava):
        return random.choice(humeurs[humeur_id]["phrases"]) + " Et toi ?"

    if any(w in content for w in quoi):
        return random.choice([
            "Je réfléchis un peu.",
            "Je t’observe.",
            "Je change d’humeur peut-être.",
            "Je traîne ici.",
            "Je regarde les messages."
        ]) + " Et toi ?"

    return None

# ================= MOOD LOOP =================

@tasks.loop(minutes=5)
async def mood_loop():
    global last_change
    if time.time() - last_change >= 7200:
        for user in humeurs_users:
            humeurs_users[user] = random.randint(1,20)
        last_change = time.time()
        save()

@bot.event
async def on_ready():
    mood_loop.start()
    print("Nameki prête 💚")

# ================= MESSAGE EVENT =================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if bot.user not in message.mentions:
        await bot.process_commands(message)
        return

    content = message.content.lower()
    user_id = str(message.author.id)

    insultes = ["con","connasse","salope","tg","ferme ta gueule","idiot","débile"]

    if any(i in content for i in insultes):
        affinite[user_id] = affinite.get(user_id,0) - 2
        save()
        return

    if user_id not in affinite:
        affinite[user_id] = 0

    if user_id not in humeurs_users:
        humeurs_users[user_id] = random.randint(1,20)

    humeur = humeurs_users[user_id]

    if affinite[user_id] > 5:
        humeur = random.choice([1,3,17,19])
    elif affinite[user_id] < -3:
        humeur = random.choice([8,12,15,18])

    if humeur in [8,13,16,20] and random.random() < 0.3:
        return

    async with message.channel.typing():
        await asyncio.sleep(random.uniform(2,4))

    reply = smart_response(content, humeur)

    if not reply:
        reply = random.choice(humeurs[humeur]["phrases"]) + " Et toi ?"

    affinite[user_id] += 1
    save()

    await message.reply(reply, mention_author=False)
    await bot.process_commands(message)

bot.run(TOKEN)
