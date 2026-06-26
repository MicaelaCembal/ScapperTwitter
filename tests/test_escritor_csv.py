"""
Tests para salida/escritor_csv.py
"""

import csv
import pytest
from pathlib import Path
from salida.escritor_csv import EscritorCSV
from modelos.esquema import Noticia, Medio, Autor, Tema, Verificacion, RelPublica


@pytest.fixture
def carpeta_tmp(tmp_path):
    return str(tmp_path / "test_datos")


def test_crea_archivos_csv(carpeta_tmp):
    with EscritorCSV(carpeta_tmp) as escritor:
        pass
    archivos = list(Path(carpeta_tmp).glob("*.csv"))
    nombres = [a.name for a in archivos]
    assert "noticias.csv" in nombres
    assert "medios.csv" in nombres
    assert "autores.csv" in nombres
    assert "temas.csv" in nombres
    assert "verificaciones.csv" in nombres
    assert "rel_publica.csv" in nombres


def test_escribir_noticia(carpeta_tmp):
    n = Noticia(noticia_id="tw_1", url="https://x.com", titulo="T", cuerpo="C",
                fecha_publicacion="2026-01-01", fecha_modificacion="2026-01-01",
                seccion="tweet", medio_id="twitter")
    with EscritorCSV(carpeta_tmp) as escritor:
        result = escritor.escribir_noticia(n)
    assert result is True
    rows = list(csv.DictReader(open(Path(carpeta_tmp) / "noticias.csv")))
    assert rows[0]["noticia_id"] == "tw_1"
    assert rows[0]["medio_id"] == "twitter"


def test_no_duplicados(carpeta_tmp):
    n = Noticia(noticia_id="tw_dup", url="https://x.com", titulo="T", cuerpo="C",
                fecha_publicacion="2026-01-01", fecha_modificacion="2026-01-01",
                seccion="tweet", medio_id="twitter")
    with EscritorCSV(carpeta_tmp) as escritor:
        r1 = escritor.escribir_noticia(n)
        r2 = escritor.escribir_noticia(n)  # duplicado
    assert r1 is True
    assert r2 is False
    rows = list(csv.DictReader(open(Path(carpeta_tmp) / "noticias.csv")))
    assert len(rows) == 1


def test_escribir_medio(carpeta_tmp):
    with EscritorCSV(carpeta_tmp) as escritor:
        escritor.escribir_medio(Medio())
    rows = list(csv.DictReader(open(Path(carpeta_tmp) / "medios.csv")))
    assert rows[0]["medio_id"] == "twitter"


def test_escribir_autor(carpeta_tmp):
    a = Autor(autor_id="tw_user_x", nombre="X", username="x")
    with EscritorCSV(carpeta_tmp) as escritor:
        escritor.escribir_autor(a)
    rows = list(csv.DictReader(open(Path(carpeta_tmp) / "autores.csv")))
    assert rows[0]["autor_id"] == "tw_user_x"


def test_escribir_tema(carpeta_tmp):
    t = Tema(tema_id="tw_tema_test", nombre="test")
    with EscritorCSV(carpeta_tmp) as escritor:
        escritor.escribir_tema(t)
    rows = list(csv.DictReader(open(Path(carpeta_tmp) / "temas.csv")))
    assert rows[0]["nombre"] == "test"


def test_persistencia_entre_sesiones(carpeta_tmp):
    """Los CSVs se deben poder abrir en append mode sin perder datos."""
    n1 = Noticia(noticia_id="tw_a", url="u", titulo="t", cuerpo="c",
                 fecha_publicacion="d", fecha_modificacion="d", seccion="tweet", medio_id="twitter")
    n2 = Noticia(noticia_id="tw_b", url="u", titulo="t", cuerpo="c",
                 fecha_publicacion="d", fecha_modificacion="d", seccion="tweet", medio_id="twitter")
    with EscritorCSV(carpeta_tmp) as e:
        e.escribir_noticia(n1)
    with EscritorCSV(carpeta_tmp) as e:
        e.escribir_noticia(n2)
        e.escribir_noticia(n1)  # duplicado entre sesiones
    rows = list(csv.DictReader(open(Path(carpeta_tmp) / "noticias.csv")))
    assert len(rows) == 2
