"""
Parseador de tweets: convierte un objeto tweet de twscrape
al esquema de nodos/relaciones del proyecto.
"""

import re
import unicodedata
from datetime import timezone
from modelos.esquema import (
    Noticia, Autor, Tema, Verificacion,
    RelEscritoPor, RelMenciona, RelVerifica,
)


# ── Clasificador de oraciones (igual al de Infobae) ───────────────────────────

_RE_CITA = re.compile(r'["\'«»]|dijo|afirmó|declaró|según|aseguró|manifestó', re.IGNORECASE)
_RE_ESTADISTICA = re.compile(r'\d+[\.,]?\d*\s*(%|por ciento|millones?|miles?|casos?|muertes?|votos?)', re.IGNORECASE)


def _clasificar_oracion(texto: str) -> str:
    if _RE_ESTADISTICA.search(texto):
        return "estadistica"
    if _RE_CITA.search(texto):
        return "cita"
    return "sin_clasificar"


def _normalizar_id(texto: str) -> str:
    """Convierte texto a slug válido para IDs."""
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^\w]", "_", texto.lower())
    return re.sub(r"_+", "_", texto).strip("_")


def _tipo_tweet(tweet) -> str:
    """Infiere el tipo de tweet para el campo 'seccion'."""
    if hasattr(tweet, "retweetedTweet") and tweet.retweetedTweet:
        return "retweet"
    if hasattr(tweet, "inReplyToTweetId") and tweet.inReplyToTweetId:
        return "reply"
    if hasattr(tweet, "quotedTweet") and tweet.quotedTweet:
        return "quote"
    return "tweet"


# ── Parseador principal ────────────────────────────────────────────────────────

def parsear_tweet(tweet) -> dict:
    """
    Recibe un objeto Tweet de twscrape y devuelve un dict con:
      - noticia: Noticia
      - autor: Autor
      - temas: list[Tema]
      - verificaciones: list[Verificacion]
      - relaciones: dict con listas de relaciones
    """
    tweet_id = str(tweet.id)
    noticia_id = f"tw_{tweet_id}"
    texto = tweet.rawContent or ""

    # Limpiar URLs del texto para el título
    texto_limpio = re.sub(r"https?://\S+", "", texto).strip()
    titulo = texto_limpio[:100] + ("…" if len(texto_limpio) > 100 else "")

    # Fecha
    fecha_dt = tweet.date
    if fecha_dt.tzinfo is None:
        fecha_dt = fecha_dt.replace(tzinfo=timezone.utc)
    fecha_iso = fecha_dt.isoformat()

    # Usuario
    user = tweet.user
    username = user.username if user else "desconocido"
    autor_id = f"tw_user_{_normalizar_id(username)}"

    noticia = Noticia(
        noticia_id=noticia_id,
        url=f"https://twitter.com/{username}/status/{tweet_id}",
        titulo=titulo,
        cuerpo=texto,
        fecha_publicacion=fecha_iso,
        fecha_modificacion=fecha_iso,
        seccion=_tipo_tweet(tweet),
        medio_id="twitter",
        likes=getattr(tweet, "likeCount", 0) or 0,
        retweets=getattr(tweet, "retweetCount", 0) or 0,
        replies=getattr(tweet, "replyCount", 0) or 0,
        views=getattr(tweet, "viewCount", 0) or 0,
        idioma=getattr(tweet, "lang", "") or "",
        es_verificado=getattr(user, "verified", False) if user else False,
    )

    autor = Autor(
        autor_id=autor_id,
        nombre=user.displayname if user else username,
        username=username,
        seguidores=getattr(user, "followersCount", 0) or 0,
        verificado=getattr(user, "verified", False) if user else False,
    )

    # Hashtags → Temas
    temas = []
    hashtags = getattr(tweet, "hashtags", []) or []
    for ht in hashtags:
        tag_norm = _normalizar_id(ht)
        temas.append(Tema(
            tema_id=f"tw_tema_{tag_norm}",
            nombre=ht.lower().lstrip("#"),
        ))

    # Oraciones → Verificaciones (igual que Infobae/Clarín)
    oraciones = [s.strip() for s in re.split(r"[.!?]\s+", texto) if len(s.strip()) > 20]
    verificaciones = []
    for idx, oracion in enumerate(oraciones):
        verificaciones.append(Verificacion(
            verificacion_id=f"tw_verif_{tweet_id}_{idx}",
            texto=oracion,
            tipo=_clasificar_oracion(oracion),
            verificado=False,
        ))

    # Relaciones
    relaciones = {
        "escrito_por": RelEscritoPor(noticia_id=noticia_id, autor_id=autor_id),
        "menciona": [RelMenciona(noticia_id=noticia_id, tema_id=t.tema_id) for t in temas],
        "verifica": [RelVerifica(verificacion_id=v.verificacion_id, noticia_id=noticia_id) for v in verificaciones],
    }

    return {
        "noticia": noticia,
        "autor": autor,
        "temas": temas,
        "verificaciones": verificaciones,
        "relaciones": relaciones,
    }
