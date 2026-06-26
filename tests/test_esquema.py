"""
Tests para el módulo modelos/esquema.py
"""

import pytest
from modelos.esquema import (
    Noticia, Medio, Autor, Tema, Verificacion,
    RelPublica, RelEscritoPor, RelMenciona, RelVerifica,
)


def test_medio_defaults():
    m = Medio()
    assert m.medio_id == "twitter"
    assert m.nombre == "Twitter / X"
    assert "twitter.com" in m.url


def test_noticia_campos():
    n = Noticia(
        noticia_id="tw_123",
        url="https://twitter.com/user/status/123",
        titulo="Esto es un tweet de prueba",
        cuerpo="Texto completo del tweet de prueba para test.",
        fecha_publicacion="2026-01-01T00:00:00+00:00",
        fecha_modificacion="2026-01-01T00:00:00+00:00",
        seccion="tweet",
        medio_id="twitter",
    )
    assert n.noticia_id == "tw_123"
    assert n.medio_id == "twitter"
    assert n.seccion == "tweet"
    assert n.likes == 0  # default


def test_autor_campos():
    a = Autor(autor_id="tw_user_usuario", nombre="Usuario Test", username="usuario")
    assert a.autor_id == "tw_user_usuario"
    assert a.username == "usuario"
    assert a.seguidores == 0  # default
    assert a.verificado is False


def test_tema_campos():
    t = Tema(tema_id="tw_tema_fakenews", nombre="fakenews")
    assert t.tema_id == "tw_tema_fakenews"
    assert t.nombre == "fakenews"


def test_verificacion_tipos_validos():
    tipos = ["cita", "estadistica", "sin_clasificar"]
    for tipo in tipos:
        v = Verificacion(verificacion_id="tw_verif_1_0", texto="Texto.", tipo=tipo)
        assert v.tipo == tipo


def test_relaciones():
    r1 = RelPublica(medio_id="twitter", noticia_id="tw_123")
    assert r1.medio_id == "twitter"

    r2 = RelEscritoPor(noticia_id="tw_123", autor_id="tw_user_alguien")
    assert r2.noticia_id == "tw_123"

    r3 = RelMenciona(noticia_id="tw_123", tema_id="tw_tema_test")
    assert r3.tema_id == "tw_tema_test"

    r4 = RelVerifica(verificacion_id="tw_verif_123_0", noticia_id="tw_123")
    assert r4.verificacion_id == "tw_verif_123_0"


def test_noticia_es_serializable():
    """Verificar que vars() funcione correctamente para el escritor CSV."""
    n = Noticia(noticia_id="tw_999", url="https://x.com", titulo="T", cuerpo="C",
                fecha_publicacion="2026-01-01", fecha_modificacion="2026-01-01",
                seccion="tweet", medio_id="twitter")
    d = vars(n)
    assert "noticia_id" in d
    assert "likes" in d
    assert "retweets" in d
