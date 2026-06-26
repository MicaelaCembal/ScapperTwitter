"""
Recolector de tweets usando twscrape.
Soporta búsqueda por query/hashtag y scraping de perfil de usuario.
"""

import asyncio
import time
from typing import AsyncIterator

import twscrape
from twscrape import API, gather
from twscrape.logger import set_log_level

from modelos.esquema import Medio, RelPublica
from salida.escritor_csv import EscritorCSV
from scraper.parseador_tweet import parsear_tweet


set_log_level("ERROR")  # Silenciar logs de twscrape en uso normal


class TwitterScraper:
    def __init__(self, carpeta_salida: str = "datos", delay: float = 2.0):
        self.carpeta_salida = carpeta_salida
        self.delay = delay
        self.api = API()

    async def agregar_cuenta(self, username: str, password: str, email: str, email_password: str):
        """
        Agrega una cuenta de Twitter para autenticación.
        twscrape necesita al menos una cuenta logueada para funcionar.
        """
        await self.api.pool.add_account(username, password, email, email_password)
        await self.api.pool.login_all()

    async def _guardar_tweet(self, tweet, escritor: EscritorCSV) -> bool:
        """Parsea un tweet y lo guarda en los CSVs. Retorna True si fue nuevo."""
        try:
            datos = parsear_tweet(tweet)
        except Exception as e:
            print(f"  [!] Error parseando tweet {tweet.id}: {e}")
            return False

        # Nodos
        escritor.escribir_medio(Medio())
        escritor.escribir_noticia(datos["noticia"])
        escritor.escribir_autor(datos["autor"])
        for tema in datos["temas"]:
            escritor.escribir_tema(tema)
        for verif in datos["verificaciones"]:
            escritor.escribir_verificacion(verif)

        # Relaciones
        escritor.escribir_rel_publica(RelPublica(noticia_id=datos["noticia"].noticia_id))
        escritor.escribir_rel_escrito_por(datos["relaciones"]["escrito_por"])
        for rel in datos["relaciones"]["menciona"]:
            escritor.escribir_rel_menciona(rel)
        for rel in datos["relaciones"]["verifica"]:
            escritor.escribir_rel_verifica(rel)

        escritor.flush()
        return True

    async def scrapear_busqueda(self, query: str, max_tweets: int = 100) -> int:
        """
        Busca tweets por query o hashtag y los guarda en CSVs.
        Ejemplo: query="#FakeNews lang:es", max_tweets=200
        """
        print(f"\n🔍 Buscando: '{query}' (máx. {max_tweets})")
        count = 0

        with EscritorCSV(self.carpeta_salida) as escritor:
            async for tweet in self.api.search(query, limit=max_tweets):
                guardado = await self._guardar_tweet(tweet, escritor)
                if guardado:
                    count += 1
                    if count % 10 == 0:
                        print(f"  → {count} tweets recopilados...")
                await asyncio.sleep(self.delay)

        print(f"✅ Búsqueda finalizada: {count} tweets nuevos guardados en '{self.carpeta_salida}/'")
        return count

    async def scrapear_usuario(self, username: str, max_tweets: int = 50) -> int:
        """
        Scrapea los tweets recientes de un usuario específico.
        Ejemplo: username="infobae", max_tweets=50
        """
        username = username.lstrip("@")
        print(f"\n👤 Scrapeando perfil: @{username} (máx. {max_tweets})")
        count = 0

        # Primero obtenemos el user_id
        user = await self.api.user_by_login(username)
        if not user:
            print(f"  [!] No se encontró el usuario @{username}")
            return 0

        with EscritorCSV(self.carpeta_salida) as escritor:
            async for tweet in self.api.user_tweets(user.id, limit=max_tweets):
                guardado = await self._guardar_tweet(tweet, escritor)
                if guardado:
                    count += 1
                    if count % 10 == 0:
                        print(f"  → {count} tweets recopilados...")
                await asyncio.sleep(self.delay)

        print(f"✅ Perfil finalizado: {count} tweets nuevos guardados en '{self.carpeta_salida}/'")
        return count

    async def scrapear_tweet_individual(self, tweet_id: str) -> int:
        """Scrapea un tweet individual por su ID o URL."""
        # Extraer ID si se pasó una URL
        import re
        match = re.search(r"status/(\d+)", tweet_id)
        if match:
            tweet_id = match.group(1)

        print(f"\n🐦 Scrapeando tweet: {tweet_id}")

        tweet = await self.api.tweet_details(int(tweet_id))
        if not tweet:
            print(f"  [!] No se encontró el tweet {tweet_id}")
            return 0

        with EscritorCSV(self.carpeta_salida) as escritor:
            guardado = await self._guardar_tweet(tweet, escritor)

        if guardado:
            print(f"✅ Tweet guardado en '{self.carpeta_salida}/'")
            return 1
        print("  [!] El tweet ya existía en los datos.")
        return 0
