"""
Dataclasses del modelo de datos para el TwitterScraper.
Mantiene compatibilidad con el esquema de InfobaeScraper y ClarinScraper
para unificación en Neo4j.
"""

from dataclasses import dataclass, field
from typing import Optional


# ── Nodos ──────────────────────────────────────────────────────────────────────

@dataclass
class Medio:
    medio_id: str = "twitter"
    nombre: str = "Twitter / X"
    url: str = "https://twitter.com"


@dataclass
class Noticia:
    """
    Representa un tweet como si fuera una noticia.
    Campos equivalentes a los de Infobae/Clarín para compatibilidad Neo4j.
    """
    noticia_id: str = ""          # tweet_id con prefijo "tw_"
    url: str = ""                  # https://twitter.com/usuario/status/id
    titulo: str = ""               # Primeros 100 chars del texto
    cuerpo: str = ""               # Texto completo del tweet
    fecha_publicacion: str = ""    # ISO 8601
    fecha_modificacion: str = ""   # Igual a publicacion (tweets no se editan)
    seccion: str = ""              # Tipo: tweet / retweet / reply / quote
    medio_id: str = "twitter"
    # Campos extra específicos de Twitter
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    views: int = 0
    idioma: str = ""
    es_verificado: bool = False    # Cuenta verificada (marca azul)


@dataclass
class Autor:
    autor_id: str = ""             # "tw_user_" + username
    nombre: str = ""               # Display name
    username: str = ""             # @handle sin @
    seguidores: int = 0
    verificado: bool = False


@dataclass
class Tema:
    tema_id: str = ""              # "tw_tema_" + hashtag normalizado
    nombre: str = ""               # hashtag sin #


@dataclass
class Verificacion:
    """
    Representa una oración del tweet clasificada para análisis de verificabilidad.
    Compatible con el esquema de Infobae/Clarín.
    """
    verificacion_id: str = ""      # "tw_verif_" + noticia_id + "_" + idx
    texto: str = ""
    tipo: str = "sin_clasificar"   # cita | estadistica | sin_clasificar
    verificado: bool = False


# ── Relaciones ─────────────────────────────────────────────────────────────────

@dataclass
class RelPublica:
    medio_id: str = "twitter"
    noticia_id: str = ""


@dataclass
class RelEscritoPor:
    noticia_id: str = ""
    autor_id: str = ""


@dataclass
class RelMenciona:
    noticia_id: str = ""
    tema_id: str = ""


@dataclass
class RelVerifica:
    verificacion_id: str = ""
    noticia_id: str = ""
