"""
Escritura incremental de CSVs compatible con InfobaeScraper y ClarinScraper.
Los campos son idénticos; la única diferencia es medio_id = "twitter".
"""

import csv
import os
from pathlib import Path
from modelos.esquema import (
    Noticia, Medio, Autor, Tema, Verificacion,
    RelPublica, RelEscritoPor, RelMenciona, RelVerifica,
)


ARCHIVOS = {
    "noticias":       ("noticias.csv",       ["noticia_id", "url", "titulo", "cuerpo", "fecha_publicacion", "fecha_modificacion", "seccion", "medio_id", "likes", "retweets", "replies", "views", "idioma", "es_verificado"]),
    "medios":         ("medios.csv",          ["medio_id", "nombre", "url"]),
    "autores":        ("autores.csv",         ["autor_id", "nombre", "username", "seguidores", "verificado"]),
    "temas":          ("temas.csv",           ["tema_id", "nombre"]),
    "verificaciones": ("verificaciones.csv",  ["verificacion_id", "texto", "tipo", "verificado"]),
    "rel_publica":    ("rel_publica.csv",      ["medio_id", "noticia_id"]),
    "rel_escrito_por":("rel_escrito_por.csv", ["noticia_id", "autor_id"]),
    "rel_menciona":   ("rel_menciona.csv",    ["noticia_id", "tema_id"]),
    "rel_verifica":   ("rel_verifica.csv",    ["verificacion_id", "noticia_id"]),
}


class EscritorCSV:
    def __init__(self, carpeta_salida: str = "datos"):
        self.carpeta = Path(carpeta_salida)
        self.carpeta.mkdir(parents=True, exist_ok=True)
        self._writers: dict = {}
        self._files: dict = {}
        self._ids_vistos: dict = {k: set() for k in ARCHIVOS}
        self._inicializar_archivos()

    def _inicializar_archivos(self):
        for clave, (nombre, campos) in ARCHIVOS.items():
            ruta = self.carpeta / nombre
            ya_existe = ruta.exists()
            f = open(ruta, "a", newline="", encoding="utf-8")
            writer = csv.DictWriter(f, fieldnames=campos)
            if not ya_existe:
                writer.writeheader()
            self._files[clave] = f
            self._writers[clave] = writer

            # Cargar IDs ya existentes para evitar duplicados
            if ya_existe:
                with open(ruta, "r", encoding="utf-8") as rf:
                    reader = csv.DictReader(rf)
                    id_field = campos[0]  # El primer campo siempre es el ID
                    for row in reader:
                        if id_field in row:
                            self._ids_vistos[clave].add(row[id_field])

    def _escribir(self, clave: str, obj, id_val: str):
        if id_val in self._ids_vistos[clave]:
            return False
        self._ids_vistos[clave].add(id_val)
        self._writers[clave].writerow(vars(obj))
        return True

    def escribir_noticia(self, n: Noticia) -> bool:
        return self._escribir("noticias", n, n.noticia_id)

    def escribir_medio(self, m: Medio) -> bool:
        return self._escribir("medios", m, m.medio_id)

    def escribir_autor(self, a: Autor) -> bool:
        return self._escribir("autores", a, a.autor_id)

    def escribir_tema(self, t: Tema) -> bool:
        return self._escribir("temas", t, t.tema_id)

    def escribir_verificacion(self, v: Verificacion) -> bool:
        return self._escribir("verificaciones", v, v.verificacion_id)

    def escribir_rel_publica(self, r: RelPublica) -> bool:
        key = f"{r.medio_id}_{r.noticia_id}"
        return self._escribir("rel_publica", r, key)

    def escribir_rel_escrito_por(self, r: RelEscritoPor) -> bool:
        key = f"{r.noticia_id}_{r.autor_id}"
        return self._escribir("rel_escrito_por", r, key)

    def escribir_rel_menciona(self, r: RelMenciona) -> bool:
        key = f"{r.noticia_id}_{r.tema_id}"
        return self._escribir("rel_menciona", r, key)

    def escribir_rel_verifica(self, r: RelVerifica) -> bool:
        key = f"{r.verificacion_id}_{r.noticia_id}"
        return self._escribir("rel_verifica", r, key)

    def flush(self):
        for f in self._files.values():
            f.flush()

    def cerrar(self):
        for f in self._files.values():
            f.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.cerrar()
