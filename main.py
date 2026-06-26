"""
TwitterScraper — Punto de entrada CLI
Parte del proyecto: Plataforma Inteligente para la Detección de
Tendencias Emergentes y Desinformación Digital

Uso:
  # Tweet individual (por URL o ID)
  python main.py --url https://twitter.com/usuario/status/123456789

  # Búsqueda por query o hashtag
  python main.py --query "#FakeNews lang:es" --max 200

  # Perfil de usuario
  python main.py --usuario infobae --max 50

  # Opciones avanzadas
  python main.py --query "desinformacion" --max 500 --salida mis_datos --delay 3.0

Configuración de cuenta (necesaria la primera vez):
  python main.py --agregar-cuenta
"""

import argparse
import asyncio
import sys
from scraper.recolector import TwitterScraper


def parse_args():
    parser = argparse.ArgumentParser(
        description="TwitterScraper — recolector de tweets para Neo4j",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--url",     metavar="URL_O_ID",  help="URL o ID de un tweet individual")
    grupo.add_argument("--query",   metavar="QUERY",     help="Query de búsqueda (ej: '#FakeNews lang:es')")
    grupo.add_argument("--usuario", metavar="USERNAME",  help="Perfil de usuario a scrapear (ej: infobae)")

    parser.add_argument("--max",    type=int, default=100, metavar="N",     help="Máximo de tweets a recolectar (default: 100)")
    parser.add_argument("--salida", default="datos",       metavar="DIR",   help="Carpeta de salida para los CSVs (default: datos/)")
    parser.add_argument("--delay",  type=float, default=2.0, metavar="SEG", help="Segundos entre requests (default: 2.0, no bajar de 1.5)")

    parser.add_argument(
        "--agregar-cuenta",
        action="store_true",
        help="Modo interactivo para agregar una cuenta de Twitter"
    )

    return parser.parse_args()


async def agregar_cuenta_interactivo(scraper: TwitterScraper):
    print("\n── Agregar cuenta de Twitter ──")
    print("twscrape necesita una cuenta para autenticarse.")
    print("Se recomienda usar una cuenta secundaria, no la principal.\n")
    username      = input("Username (sin @): ").strip()
    password      = input("Password: ").strip()
    email         = input("Email de la cuenta: ").strip()
    email_password = input("Password del email: ").strip()
    print("\nIniciando sesión...")
    await scraper.agregar_cuenta(username, password, email, email_password)
    print("✅ Cuenta agregada. Ya podés usar el scraper.")


async def main():
    args = parse_args()
    scraper = TwitterScraper(carpeta_salida=args.salida, delay=args.delay)

    if args.agregar_cuenta:
        await agregar_cuenta_interactivo(scraper)
        return

    if not args.url and not args.query and not args.usuario:
        print("Error: debés especificar --url, --query, --usuario, o --agregar-cuenta")
        print("Usá --help para ver las opciones disponibles.")
        sys.exit(1)

    if args.url:
        await scraper.scrapear_tweet_individual(args.url)
    elif args.query:
        await scraper.scrapear_busqueda(args.query, max_tweets=args.max)
    elif args.usuario:
        await scraper.scrapear_usuario(args.usuario, max_tweets=args.max)


if __name__ == "__main__":
    asyncio.run(main())
