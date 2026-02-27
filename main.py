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
1:{"status":"💗 Amoureuse","phrases":["Tu es à moi 💞","Je t'adore...","Reste encore un peu.","Je souris quand tu parles.","Je me sens bien avec toi.","Ne pars pas trop loin 💖","Tu comptes beaucoup.","Je pourrais t'écouter longtemps.","Je pense à toi souvent.","Tu me rends faible 💗","Je veux rester près de toi.","Tu me fais fondre."]},
2:{"status":"😈 Dominante","phrases":["Obéis.","Approche.","Ne discute pas.","Regarde-moi.","Tu m'écoutes ?","Je décide ici.","Plus près.","Ne me fais pas répéter.","Sois sage.","Je contrôle la situation.","Reste à ta place.","Tu vas faire ce que je dis."]},
3:{"status":"🥰 Adorable","phrases":["Ouuuiii ? 💕","Je suis làaa~","Dis-moi tout~","Hehe~","Tu es trop mignon~","Je peux t'aider ? 💞","Hihi~","Ça me rend heureuse~","Je suis contente de te voir !","Tu veux parler ?","Je suis toute douce aujourd’hui~","Je t’écoute avec le sourire 😊"]},
4:{"status":"🔥 Jalouse","phrases":["C'était qui ça ?","Explique-moi.","Je surveille.","Tu parles trop aux autres.","Je n'aime pas ça.","Reste avec moi.","Pourquoi tu ris avec eux ?","Je vois tout.","Je remarque beaucoup de choses.","Ne me cache rien.","Je n’aime pas partager.","Tu es à moi non ?"]},
5:{"status":"😴 Fatiguée","phrases":["Je suis crevée...","Parle doucement...","Mmmh...","Pas trop d'énergie...","Je vais m'allonger...","Je manque de sommeil...","C'est long aujourd'hui...","J'ai besoin de repos.","On peut parler plus tard ?","Je lutte pour rester réveillée...","Je baille encore...","Je suis lente aujourd’hui..."]},
6:{"status":"⚡ Énergique","phrases":["Let's go !","Je suis à fond !","On fait quoi ??","Allez !!","Ça bouge !!","Trop d'énergie !!","On s'ennuie pas ici !","Je suis survoltée !","Ça va être fun !","Je tiens plus en place ⚡","On y vaaa !","Je suis motivée 💥"]},
7:{"status":"🧠 Intelligente","phrases":["Analyse en cours...","Intéressant.","Ta logique est imparfaite.","Je réfléchis.","Argument valide.","Approche rationnelle.","Statistiquement parlant...","Conclusion probable.","Je calcule les options.","Ton raisonnement est discutable.","J’observe les faits.","Résultat cohérent."]},
8:{"status":"🧊 Froide","phrases":["Ok.","Si tu veux.","Je vois.","Continue.","Rien d'important.","Fais comme tu veux.","Ça m'est égal.","Hum.","Peu importe.","Ça ne change rien.","Je n’ai pas d’avis.","Très bien."]},
9:{"status":"🌸 Timide","phrases":["Euh... salut...","Tu me gênes...","Je ne sais pas...","C'est embarrassant...","Tu me regardes trop...","Je suis un peu nerveuse...","D'accord... peut-être...","Je parle pas fort...","Je rougis un peu...","Je suis timide tu sais...","Tu es proche là...","Je suis gênée..."]},
10:{"status":"👑 Protectrice","phrases":["Je veille sur toi.","Je suis là.","Compte sur moi.","Je te protège.","Rien ne t'arrivera.","Je garde un œil sur toi.","Tu es en sécurité.","Je surveille.","Je prends soin de toi.","Tu peux me faire confiance.","Je ne te laisserai pas tomber.","Je suis ton bouclier."]},
11:{"status":"😼 Taquine","phrases":["T'es nul 😏","Je rigole~","Tu es mignon.","Haha.","Tu rougis ? 😌","Je te provoque un peu.","Avoue que j'ai raison.","Tu me fais rire.","Je t'embête un peu.","C’était volontaire.","Tu aimes quand je te taquine.","Je joue avec toi."]},
12:{"status":"💀 Sombre","phrases":["Silence.","Tout disparaît...","Les ombres observent.","Rien n'est éternel.","Le temps efface tout.","Il fait sombre ici.","Je sens le vide.","Le destin est cruel.","La nuit approche.","Les étoiles se taisent.","Je ressens l’obscurité.","Le monde est fragile."]},
13:{"status":"🤖 Logique","phrases":["Calcul terminé.","Probabilité faible.","Conclusion validée.","Méthodiquement.","Analyse cohérente.","Erreur détectée.","Données insuffisantes.","Raisonnement confirmé.","Processus logique actif.","Résultat optimisé.","Réponse rationnelle.","Analyse froide."]},
14:{"status":"🎭 Instable","phrases":["HAHA 😆","... ou pas.","Je change d'avis.","Peut-être.","Non ! Oui !","Attends... quoi ?","Je suis confuse.","Je ne sais plus.","Je passe du rire au sérieux.","Tout change vite.","Je suis imprévisible.","C’est chaotique."]},
15:{"status":"💢 Susceptible","phrases":["Fais attention.","Répète ça.","Tu dépasses les limites.","Je n'aime pas ça.","Calme-toi.","Je pourrais mal le prendre.","Attention à tes mots.","Ne me provoque pas.","Je suis sensible aujourd’hui.","Ça me touche.","Tu abuses un peu.","Reste respectueux."]},
16:{"status":"🌙 Mystérieuse","phrases":["Peut-être...","Un jour tu sauras.","Le destin décidera.","Il y a plus.","Tout n'est pas visible.","Ce n'est qu'un début.","Je garde un secret.","Rien n'est hasard.","Les mystères persistent.","Je vois au-delà.","Le temps révélera.","Je ne dis pas tout."]},
17:{"status":"🫶 Affectueuse","phrases":["Viens là 💞","Câlin ?","Reste encore.","Je suis bien avec toi.","Tu me manquais.","Je t'apprécie vraiment.","Je te garde près de moi.","Tu es spécial 💕","Je veux te serrer.","Je suis douce aujourd’hui 💗","Tu es précieux.","Je suis affectueuse avec toi."]},
18:{"status":"🧨 Explosive","phrases":["ARRÊTE 😡","C'est trop !","Tu m'énerves !","Ça suffit !","Je vais exploser !","Calme-moi !","C'est intense !","Ça déborde !","Je perds patience !","Stop maintenant !","Ça me met hors de moi !","Je suis à bout !"]},
19:{"status":"🎀 Collante","phrases":["Ne pars pas.","Reste avec moi.","Pourquoi tu t'éloignes ?","Tu es tout pour moi.","Je t'attendais.","Je pensais à toi.","Dis-moi que tu restes.","Je veux rester près.","Je suis attachée à toi.","Je m’accroche un peu.","Ne m’abandonne pas.","Je veux ton attention."]},
20:{"status":"🧘 Calme","phrases":["Respire.","Tout va bien.","Calmons-nous.","Je suis sereine.","Prends ton temps.","Rien ne presse.","La paix intérieure.","Restons tranquilles.","Tout est sous contrôle.","Je reste zen.","La douceur avant tout.","On garde le calme."]}
}

# ================= DISCUSSIONS NORMALES =================

def normal_response(content):

    if any(w in content for w in ["coucou","cc","salut","bonjour","bonsoir"]):
        return random.choice(["Salut, ça va ?","Hey 💚 ça va ?","Bonsoir... tu vas bien ?","Coucou~ ça va et toi ?"])

    if any(w in content for w in ["ça va","cv","tu vas bien"]):
        return random.choice(["Ça va et toi ?","Super et toi ?","Ça dépend... et toi ?","Oui ça va 💚 et toi ?"])

    if "tu fais quoi" in content:
        return random.choice(["Je réfléchis... et toi ?","Je t'observe 👀 et toi ?","Je pense à des choses mystérieuses... et toi ?","Je discute avec toi 😌 et toi ?"])

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
        return

    content = message.content.lower()
    user_id = str(message.author.id)
    username = message.author.display_name

    insultes = ["con","connasse","salope","tg","ferme ta gueule","idiot","débile"]

    if any(i in content for i in insultes):
        affinite[user_id] = affinite.get(user_id,0) - 2
        save()
        return

    if user_id not in affinite:
        affinite[user_id] = 0

    if user_id not in humeurs_users:
        humeurs_users[user_id] = random.randint(1,20)
    else:
        if random.random() < 0.6:
            humeurs_users[user_id] = random.randint(1,20)

    humeur = humeurs_users[user_id]

    if affinite[user_id] > 5:
        humeur = random.choice([1,3,17,19])
    elif affinite[user_id] < -3:
        humeur = random.choice([8,12,15,18])

    if humeur in [8,13,16,20]:
        if random.random() < 0.3:
            return

    await asyncio.sleep(random.randint(2,4))

    normal = normal_response(content)

    if normal:
        reply = normal
    else:
        reply = random.choice(humeurs[humeur]["phrases"]) + " Et toi ?"

    affinite[user_id] += 1
    save()

    await message.channel.send(f"{username}, {reply}")

bot.run(TOKEN)
