"""
Tests para scraper/parseador_tweet.py
Usa objetos mock para no depender de la API real.
"""

import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone
from scraper.parseador_tweet import parsear_tweet, _clasificar_oracion, _normalizar_id


# ── Helpers ───────────────────────────────────────────────────────────────────

def mock_tweet(
    tweet_id="123456789",
    texto="Esto es un tweet de prueba. Según expertos, el 30% de las noticias son falsas.",
    username="usuario_test",
    display_name="Usuario Test",
    seguidores=1000,
    verificado=False,
    hashtags=None,
    tipo_tweet="tweet",
):
    user = MagicMock()
    user.username = username
    user.displayname = display_name
    user.followersCount = seguidores
    user.verified = verificado

    tweet = MagicMock()
    tweet.id = tweet_id
    tweet.rawContent = texto
    tweet.date = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    tweet.user = user
    tweet.hashtags = hashtags or []
    tweet.likeCount = 42
    tweet.retweetCount = 10
    tweet.replyCount = 5
    tweet.viewCount = 500
    tweet.lang = "es"

    # Para _tipo_tweet
    tweet.retweetedTweet = None
    tweet.inReplyToTweetId = None
    tweet.quotedTweet = None

    return tweet


# ── Tests clasificador ────────────────────────────────────────────────────────

def test_clasificar_estadistica():
    assert _clasificar_oracion("El 40% de los casos se registraron en Buenos Aires") == "estadistica"
    assert _clasificar_oracion("Hay 3 millones de afectados") == "estadistica"


def test_clasificar_cita():
    assert _clasificar_oracion('El presidente dijo "esto es inaceptable"') == "cita"
    assert _clasificar_oracion("Según la ministra, la situación mejora") == "cita"


def test_clasificar_sin_clasificar():
    assert _clasificar_oracion("El día estuvo soleado en la capital") == "sin_clasificar"


# ── Tests normalizar ID ───────────────────────────────────────────────────────

def test_normalizar_id_basico():
    assert _normalizar_id("FakeNews") == "fakenews"
    assert _normalizar_id("Hola Mundo!") == "hola_mundo"
    assert _normalizar_id("désinformation") == "desinformation"


# ── Tests parseador ───────────────────────────────────────────────────────────

def test_parsear_tweet_estructura():
    tweet = mock_tweet()
    resultado = parsear_tweet(tweet)
    assert "noticia" in resultado
    assert "autor" in resultado
    assert "temas" in resultado
    assert "verificaciones" in resultado
    assert "relaciones" in resultado


def test_parsear_tweet_noticia():
    tweet = mock_tweet(tweet_id="999")
    datos = parsear_tweet(tweet)
    n = datos["noticia"]
    assert n.noticia_id == "tw_999"
    assert "twitter.com" in n.url
    assert n.medio_id == "twitter"
    assert n.likes == 42
    assert n.retweets == 10
    assert n.idioma == "es"


def test_parsear_tweet_autor():
    tweet = mock_tweet(username="testuser", seguidores=500)
    datos = parsear_tweet(tweet)
    a = datos["autor"]
    assert a.username == "testuser"
    assert a.autor_id == "tw_user_testuser"
    assert a.seguidores == 500


def test_parsear_tweet_hashtags():
    tweet = mock_tweet(hashtags=["FakeNews", "Desinformacion"])
    datos = parsear_tweet(tweet)
    temas = datos["temas"]
    assert len(temas) == 2
    ids = [t.tema_id for t in temas]
    assert "tw_tema_fakenews" in ids
    assert "tw_tema_desinformacion" in ids


def test_parsear_tweet_verificaciones():
    tweet = mock_tweet(
        texto="El 40% de los argentinos lee noticias digitales. Según expertos, esto genera desinformación masiva."
    )
    datos = parsear_tweet(tweet)
    verificaciones = datos["verificaciones"]
    assert len(verificaciones) >= 1
    tipos = [v.tipo for v in verificaciones]
    assert "estadistica" in tipos or "cita" in tipos


def test_parsear_tweet_sin_hashtags():
    tweet = mock_tweet(hashtags=[])
    datos = parsear_tweet(tweet)
    assert datos["temas"] == []
    assert datos["relaciones"]["menciona"] == []


def test_parsear_tweet_url_correcta():
    tweet = mock_tweet(tweet_id="555", username="miusuario")
    datos = parsear_tweet(tweet)
    assert datos["noticia"].url == "https://twitter.com/miusuario/status/555"
