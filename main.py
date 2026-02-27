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
1:{"status":"💗 Amoureuse","phrases":["Tu es à moi 💞","Je t'adore...","Reste encore un peu.","Je souris quand tu parles."]},
2:{"status":"😈 Dominante","phrases":["Obéis.","Approche.","Ne discute pas.","Regarde-moi."]},
3:{"status":"🥰 Adorable","phrases":["Ouuuiii ? 💕","Je suis làaa~","Dis-moi tout~","Hehe~"]},
4:{"status":"🔥 Jalouse","phrases":["C'était qui ça ?","Explique-moi.","Je surveille.","Reste avec moi."]},
5:{"status":"😴 Fatiguée","phrases":["Je suis crevée...","Mmmh...","Je vais m'allonger...","Je manque de sommeil..."]},
6:{"status":"⚡ Énergique","phrases":["Let's go !","Je suis à fond !","On fait quoi ??","Ça bouge !!"]},
7:{"status":"🧠 Intelligente","phrases":["Analyse en cours...","Intéressant.","Argument valide.","Je réfléchis."]},
8:{"status":"🧊 Froide","phrases":["Ok.","Si tu veux.","Hum.","Peu importe."]},
9:{"status":"🌸 Timide","phrases":["Euh... salut...","Je ne sais pas...","Je suis gênée...","D'accord..."]},
10:{"status":"👑 Protectrice","phrases":["Je veille sur toi.","Je suis là.","Je te protège.","Compte sur moi."]},
11:{"status":"😼 Taquine","phrases":["T'es nul 😏","Je rigole~","Tu es mignon.","Haha."]},
12:{"status":"💀 Sombre","phrases":["Silence.","Les ombres observent.","Rien n'est éternel.","Le temps efface tout."]},
13:{"status":"🤖 Logique","phrases":["Calcul terminé.","Conclusion validée.","Erreur détectée.","Analyse froide."]},
14:{"status":"🎭 Instable","phrases":["HAHA 😆","Je change d'avis.","Peut-être.","Je suis imprévisible."]},
15:{"status":"💢 Susceptible","phrases":["Fais attention.","Répète ça.","Ne me provoque pas.","Je suis sensible aujourd’hui."]},
16:{"status":"🌙 Mystérieuse","phrases":["Peut-être...","Un jour tu sauras.","Je garde un secret.","Rien n'est hasard."]},
17:{"status":"🫶 Affectueuse","phrases":["Viens là 💞","Câlin ?","Tu es spécial 💕","Je suis douce aujourd’hui 💗"]},
18:{"status":"🧨 Explosive","phrases":["ARRÊTE 😡","Ça suffit !","Je vais exploser !","Stop maintenant !"]},
19:{"status":"🎀 Collante","phrases":["Ne pars pas.","Reste avec moi.","Je pensais à toi.","Je suis attachée à toi."]},
20:{"status":"🧘 Calme","phrases":["Respire.","Tout va bien.","Je suis sereine.","On garde le calme."]}
}

# ================= SMART RESPONSE =================

last_response = ""

def smart_response(content, humeur_id):

    global last_response
    content = content.lower()

    saluts = ["coucou","cc","salut","bonjour","bonsoir","hey","yo"]
    cava = ["ça va","ca va","cv","tu vas bien","comment tu vas"]

    humeur_map = {
        "joyeuse":[1,3,6,17],
        "froide":[8,13,20],
        "taquine":[11,14],
        "triste":[5,12,15]
    }

    humeur_type = "joyeuse"

    for k,v in humeur_map.items():
        if humeur_id in v:
            humeur_type = k

    moods = {
        "joyeuse":{
            "salut":["Hey 💚","Coucou ✨","Hellooo~"],
            "cava":["Toujours 💚 et toi ?","Super humeur ✨ et toi ?"],
            "normal":["Intéressant 👀","Continue je t’écoute~"]
        },
        "froide":{
            "salut":["Oui ?","Hm.","Salut."],
            "cava":["Ça dépend.","Bof.","Pourquoi ?"],
            "normal":["Mouais.","Ok."]
        },
        "taquine":{
            "salut":["Tu me cherches ? 😏","Encore toi ?"],
            "cava":["Peut-être bien.","Et si je dis non ?"],
            "normal":["Hmm...","Intéressant 😏"]
        },
        "triste":{
            "salut":["Oh… salut.","Hey."],
            "cava":["Bof aujourd’hui…","Ça ira."],
            "normal":["Je vois.","Peut-être."]
        }
    }

    response_type = "normal"

    if any(w in content for w in saluts):
        response_type = "salut"
    elif any(w in content for w in cava):
        response_type = "cava"

    response = random.choice(moods[humeur_type][response_type])

    while response == last_response:
        response = random.choice(moods[humeur_type][response_type])

    last_response = response
    return response

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

    # Temps d'écriture variable selon humeur
    if humeur in [1,3,17]:
        delay = random.uniform(2.5,4.5)
    elif humeur in [8,13]:
        delay = random.uniform(1.5,3)
    else:
        delay = random.uniform(2,4)

    async with message.channel.typing():
        await asyncio.sleep(delay)

    reply = smart_response(content, humeur)

    if not reply:
        reply = random.choice(humeurs[humeur]["phrases"]) + " Et toi ?"

    affinite[user_id] += 1
    save()

    await message.channel.send(reply)

bot.run(TOKEN)
