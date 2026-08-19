"""Pruebas de la importación de datos del SIMA (issue #9).

Correr desde la raíz del repo:

    source venv/bin/activate
    pytest -v
    pytest -v -m "not lento"      # salta las que abren Excel
    pytest tests/test_importar_datos.py::test_normaliza_encabezados_de_2024
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.importar_datos import (  # noqa: E402
    COLUMNAS_BD,
    PARAMETROS,
    RUTA_PROCESSED,
    UNIDADES,
    _es_fila_de_unidades,
    _normalizar_encabezado,
    cargar_bd_anio,
    cargar_etiquetas,
    cargar_inventario,
)


# --- Normalización de encabezados -------------------------------------------

@pytest.mark.parametrize(
    ("crudo", "esperado"),
    [
        ("Fecha y hora", "fecha"),   # 2020-2024
        ("date", "fecha"),           # 2025
        ("CO (ppm)", "CO"),          # 2024 pega la unidad al nombre
        ("PM10 (ug/m3)", "PM10"),
        ("TOUT (ºC)", "TOUT"),
        ("WDR (azimutal)", "WDR"),
        ("PM2.5", "PM2.5"),
        ("PM25", "PM2.5"),
        ("  SO2  ", "SO2"),
    ],
)
def test_normaliza_encabezados_de_2024(crudo, esperado):
    assert _normalizar_encabezado(crudo) == esperado


def test_detecta_la_fila_de_unidades_de_2025():
    unidades = pd.Series({"fecha": None, "CO": "ppm", "NO": "ppb", "PM10": None})
    datos = pd.Series({"fecha": pd.Timestamp("2025-01-01"), "CO": 0.18, "NO": 2.6,
                       "PM10": 58})
    vacia = pd.Series({"fecha": None, "CO": None, "NO": None, "PM10": None})

    assert _es_fila_de_unidades(unidades)
    assert not _es_fila_de_unidades(datos)
    assert not _es_fila_de_unidades(vacia)


def test_todo_parametro_tiene_unidad_documentada():
    assert set(UNIDADES) == set(PARAMETROS)


# --- Carga de los Excel crudos ----------------------------------------------

@pytest.mark.lento
@pytest.mark.parametrize("anio", [2024, 2025])
def test_los_anios_raros_quedan_con_el_esquema_canonico(anio):
    """2024 (unidades en el encabezado) y 2025 (columna 'date' + fila de
    unidades) son los dos archivos que rompen un concat ingenuo."""
    df = cargar_bd_anio(anio)

    assert list(df.columns) == COLUMNAS_BD
    assert df["anio"].eq(anio).all()
    assert df["fecha"].notna().all(), "quedaron filas sin fecha (¿fila de unidades?)"
    assert df["fecha"].dt.year.eq(anio).all()
    assert not df.duplicated(["estacion", "fecha"]).any()
    for parametro in PARAMETROS:
        assert pd.api.types.is_numeric_dtype(df[parametro]), parametro


@pytest.mark.lento
def test_etiquetas_separa_los_cuatro_catalogos():
    catalogos = cargar_etiquetas()

    assert set(catalogos) == {"estaciones", "contaminantes", "meteorologicos",
                              "banderas"}
    # 7 parámetros meteorológicos: si salen 20+, el bloque de banderas se coló
    assert len(catalogos["meteorologicos"]) == 7
    assert "SE" in set(catalogos["estaciones"]["Abreviatura"])
    assert "PM10" in set(catalogos["contaminantes"]["Abreviatura"])


@pytest.mark.lento
def test_inventario_ignora_las_tablas_dinamicas_pegadas():
    """Las hojas traen tablas dinámicas a la derecha de la columna Q."""
    for tabla in cargar_inventario().values():
        assert tabla.shape[1] == 17
        assert not any(str(c).startswith(("Unnamed", "Suma de")) for c in tabla.columns)
        for emision in ["E_PM10", "E_PM2.5", "E_CO", "E_NOX"]:
            assert pd.api.types.is_numeric_dtype(tabla[emision]), emision


# --- Resultado consolidado ---------------------------------------------------

@pytest.mark.skipif(
    not (RUTA_PROCESSED / "sima_horario.parquet").exists(),
    reason="falta data/processed/sima_horario.parquet (corre python src/importar_datos.py)",
)
def test_el_consolidado_es_una_serie_horaria_sin_duplicados():
    df = pd.read_parquet(RUTA_PROCESSED / "sima_horario.parquet")

    assert list(df.columns) == COLUMNAS_BD
    assert df["fecha"].notna().all()
    assert not df.duplicated(["estacion", "fecha"]).any()
    assert set(df["anio"]) == {2020, 2021, 2022, 2023, 2024, 2025}
    # 15 estaciones históricas; ninguna debe aparecer con espacios o minúsculas
    estaciones = set(df["estacion"].astype(str))
    assert estaciones == {e.strip().upper() for e in estaciones}
