import os
import re
import unicodedata

import discord


def normaliser(texte: str) -> str:
    """Met en minuscules et retire les accents (é -> e, ç -> c, etc.)."""
    texte = unicodedata.normalize("NFD", texte)
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")
    return texte.lower()


# Déclencheur (écrit sans accents, en minuscules) -> réponse du bot
REPONSES = {
    "ma republique": "c'est toi",
    "macron": "explosion",
    "lait": "fraise",
    "abattez": "abattez la citadelle !",
}

# \b = limite de mot : "lait" répond dans "j'aime le lait" mais pas dans "s'il te plaît"
MOTIFS = [
    (re.compile(r"\b" + r"\s+".join(re.escape(mot) for mot in cle.split()) + r"\b"), reponse)
    for cle, reponse in REPONSES.items()
]

intents = discord.Intents.default()
intents.message_content = True  # nécessaire pour lire le texte des messages

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Connecté en tant que {client.user}")


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:  # évite que le bot se réponde à lui-même
        return

    texte = normaliser(message.content)

    # Repère chaque déclencheur présent, dans l'ordre où il apparaît dans le message
    trouves = []
    for motif, reponse in MOTIFS:
        m = motif.search(texte)
        if m:
            trouves.append((m.start(), reponse))
    trouves.sort()

    if trouves:
        await message.channel.send("\n".join(reponse for _, reponse in trouves))


client.run(os.environ["DISCORD_TOKEN"])
