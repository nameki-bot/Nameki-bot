import discord
from discord.ext import commands
import random
import asyncio
import json
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)

DATA_FILE = "data.json"

# -------------------- SAUVEGARDE --------------------

def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"affinite": {}, "humeurs": {}}

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load()
affinite = data["affinite"]
humeurs_users = data["humeurs"]

# -------------------- HUMEURS --------------------

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

INSULTES = ["tg", "ta gueule", "fdp", "connard", "pute"]

# -------------------- SMART RESPONSE --------------------

def smart_response(content):
    content = content.lower()

    if any(i in content for i in INSULTES):
        return None

    if "salut" in content or "coucou" in content or "bonjour" in content:
        return random.choice(["Coucou 💕","Salut toi.","Hey~"])

    if "ça va" in content:
        return random.choice(["Ça va et toi ?","Je vais bien.","Bof aujourd’hui."])

    return None

# -------------------- EVENTS --------------------

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user not in message.mentions:
        return

    user_id = str(message.author.id)
    content = message.content.replace(f"<@{bot.user.id}>", "").strip()

    if user_id not in affinite:
        affinite[user_id] = 0

    if user_id not in humeurs_users:
        humeurs_users[user_id] = random.randint(1, 20)

    humeur = humeurs_users[user_id]

    async with message.channel.typing():
        await asyncio.sleep(random.uniform(1.5, 3))

    reply = smart_response(content)

    if not reply:
        reply = random.choice(humeurs[humeur]["phrases"])

    affinite[user_id] += 1
    save()

    await message.channel.send(
        f"{message.author.mention} {reply}",
        allowed_mentions=discord.AllowedMentions(users=True)
    )

bot.run(TOKEN)
