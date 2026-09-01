"""Pruebas de la agregación día-estación (issue #51).

Correr desde la raíz del repo:

    uv run pytest -v tests/test_agregacion_diaria.py

Ninguna abre los Excel de data/raw/, así que no llevan el marcador `lento`. La
última depende del parquet de salida y se salta sola si no se ha generado.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agregacion_diaria import (  # noqa: E402
    CLAVE,
    ELEV,
    MIN_HORAS_DIA,
    MIN_HORAS_DIURNA,
    MIN_HORAS_PRECURSORES,
    NIVELES_TIPO_DIA,
    RESUMENES,
    RUTA_PROCESSED,
    ZONA,
    agregar_a_diario,
    calendario_festivos,
    marcar_calendario,
)
from src.limpieza import Log, MIN_VENTANAS_DIA  # noqa: E402

COLUMNAS = ["fecha", "estacion", "hora", "O3", "CO", "NO", "NO2", "NOX", "SO2",
            "PM10", "PM2.5", "TOUT", "RH", "SR", "RAINF", "PRS", "WSR", "WDR",
            "viento_u", "viento_v"]


def dia_horario(valores: dict, fecha: str = "2023-05-10",
                estacion: str = "CE") -> pd.DataFrame:
    """Un día-estación completo de 24 h; `valores` sobrescribe por variable.

    Cada entrada de `valores` es un array de 24 posiciones (una por hora); las
    variables que no se nombran quedan en NaN, que es lo que hace que el test
    mida la regla de completitud y no el relleno.
    """
    horas = pd.date_range(f"{fecha} 00:00", periods=24, freq="h")
    df = pd.DataFrame({c: np.nan for c in COLUMNAS}, index=range(24))
    df["fecha"] = horas
    df["estacion"] = estacion
    df["hora"] = horas.hour
    for k, v in valores.items():
        df[k] = np.asarray(v, dtype=float)
    return df


def agregar(df: pd.DataFrame) -> pd.Series:
    """Corre el pipeline sobre un solo día-estación y devuelve esa fila."""
    return agregar_a_diario(df, Log()).iloc[0]


# --- Regla de completitud ----------------------------------------------------

def test_la_referencia_de_completitud_es_la_del_mda8():
    """El criterio no se inventa: se hereda del MDA8 de #13 (18 de 24)."""
    assert MIN_HORAS_DIA == MIN_VENTANAS_DIA == 18
    # Las ventanas cortas conservan la misma proporción, 3/4.
    assert MIN_HORAS_PRECURSORES / 4 == MIN_HORAS_DIA / 24 == MIN_HORAS_DIURNA / 12


@pytest.mark.parametrize(("validas", "hay_valor"), [(17, False), (18, True)])
def test_el_dia_completo_exige_18_de_24_horas(validas, hay_valor):
    pm = np.full(24, 50.0)
    pm[validas:] = np.nan
    fila = agregar(dia_horario({"PM10": pm}))
    assert pd.isna(fila["PM10_media"]) is not hay_valor


@pytest.mark.parametrize(("validas", "hay_valor"), [(2, False), (3, True)])
def test_los_precursores_se_miden_sobre_la_ventana_06_09(validas, hay_valor):
    """Con las 24 h llenas salvo dentro de 06-09: la regla debe fijarse en la
    ventana, no en el día. Si mirara las 24 h, estos días pasarían."""
    nox = np.full(24, 30.0)
    for h in (6, 7, 8, 9)[validas:]:
        nox[h] = np.nan
    fila = agregar(dia_horario({"NOX": nox}))
    assert nox[~np.isnan(nox)].size >= MIN_HORAS_DIA      # el día sí está completo
    assert pd.isna(fila["NOX_06_09"]) is not hay_valor


def test_la_media_de_precursores_usa_solo_06_09():
    nox = np.full(24, 100.0)
    nox[6:10] = 10.0
    assert agregar(dia_horario({"NOX": nox}))["NOX_06_09"] == pytest.approx(10.0)


def test_sr_mide_completitud_en_la_ventana_diurna():
    """Un día con 18 de 24 horas válidas pero al que le faltan seis de tarde
    pasaría el 18/24 habiendo perdido la mitad de la energía. Debe quedar NaN."""
    sr = np.full(24, 0.0)
    sr[7:19] = 0.5
    sr[13:19] = np.nan                      # se van 6 de las 12 horas diurnas
    assert np.isfinite(sr).sum() == 18      # el criterio de 24 h sí lo aprobaría
    assert pd.isna(agregar(dia_horario({"SR": sr}))["SR_acum"])


def test_sr_es_acumulado_no_promedio():
    sr = np.zeros(24)
    sr[7:19] = 0.5                          # 12 horas de luz a 0.5 kW/m2
    assert agregar(dia_horario({"SR": sr}))["SR_acum"] == pytest.approx(6.0)


def test_rh_min_es_diurno_no_de_24_horas():
    rh = np.full(24, 60.0)
    rh[3] = 5.0                             # mínimo de madrugada: debe ignorarse
    rh[14] = 20.0                           # mínimo diurno: es el que cuenta
    assert agregar(dia_horario({"RH": rh}))["RH_min_diurna"] == pytest.approx(20.0)


def test_tout_es_el_maximo_del_dia():
    tout = np.linspace(10, 33, 24)
    assert agregar(dia_horario({"TOUT": tout}))["TOUT_max"] == pytest.approx(33.0)


# --- Viento ------------------------------------------------------------------

def test_la_media_vectorial_no_coincide_con_la_escalar_si_la_direccion_rota():
    """12 h de viento al este y 12 al oeste, misma rapidez: la media escalar de
    WSR es 10 km/h y el transporte neto es cero. Promediar WSR mediría magnitud
    sin dirección, que es justo el error que las componentes evitan."""
    wsr = np.full(24, 10.0)
    u = np.r_[np.full(12, 10.0), np.full(12, -10.0)]
    v = np.zeros(24)
    fila = agregar(dia_horario({"WSR": wsr, "viento_u": u, "viento_v": v}))

    escalar = wsr.mean()
    vectorial = np.hypot(fila["viento_u_media"], fila["viento_v_media"])
    assert escalar == pytest.approx(10.0)
    assert vectorial == pytest.approx(0.0, abs=1e-9)
    assert fila["WSR_media"] == pytest.approx(escalar)


def test_wsr_media_y_minimo_son_senales_distintas():
    wsr = np.full(24, 12.0)
    wsr[16] = 0.5                           # una hora de calma
    fila = agregar(dia_horario({"WSR": wsr}))
    assert fila["WSR_min"] == pytest.approx(0.5)
    assert fila["WSR_media"] > 11


# --- Lluvia ------------------------------------------------------------------

def test_una_sola_hora_de_lluvia_basta_para_llovio():
    rainf = np.full(24, np.nan)
    rainf[15] = 2.4                         # 1 hora válida de 24, pero llovió
    assert agregar(dia_horario({"RAINF": rainf}))["llovio"] == 1.0


def test_no_llovio_exige_el_dia_casi_completo():
    """Afirmar que NO llovió sí necesita cobertura: el aguacero pudo caer en las
    horas ausentes."""
    rainf = np.zeros(24)
    rainf[MIN_HORAS_DIA - 1:] = np.nan
    assert pd.isna(agregar(dia_horario({"RAINF": rainf}))["llovio"])

    rainf = np.zeros(24)
    rainf[MIN_HORAS_DIA:] = np.nan
    assert agregar(dia_horario({"RAINF": rainf}))["llovio"] == 0.0


# --- Catálogos geográficos ---------------------------------------------------

def test_las_15_estaciones_caen_en_las_7_zonas_del_catalogo():
    assert len(ZONA) == 15
    assert len(set(ZONA.values())) == 7
    assert set(ZONA.values()) == {"Noroeste", "Suroeste", "Noreste", "Sureste",
                                  "Norte", "Centro", "Sur"}


def test_toda_estacion_tiene_zona_y_elevacion():
    assert set(ELEV) == set(ZONA)
    assert all(300 < m < 800 for m in ELEV.values())


# --- Calendario --------------------------------------------------------------

def test_el_calendario_tiene_los_71_dias_de_asueto_de_la_cobertura():
    """El calendario genera 81 días para 2021-2025 completos, pero la serie
    termina el 2025-06-30: dentro de la ventana observada caen 71, que es la
    cifra que reporta la issue #51."""
    fest = calendario_festivos()
    assert len(fest) == 81
    dentro = [f for f in fest if pd.Timestamp("2021-01-01") <= f
              <= pd.Timestamp("2025-06-30")]
    assert len(dentro) == 71


def test_un_festivo_en_sabado_queda_como_festivo_no_como_sabado():
    # 2021-05-01 (Día del Trabajo) cae en sábado.
    df = marcar_calendario(pd.DataFrame({"fecha": pd.to_datetime(
        ["2021-05-01", "2021-05-08", "2021-05-09", "2021-05-10"])}))
    assert list(df["tipo_dia"]) == ["festivo", "sabado", "domingo", "laborable"]
    assert list(df["festivo"]) == [1, 0, 0, 0]
    assert list(df["tipo_dia"].cat.categories) == NIVELES_TIPO_DIA


# --- Resultado sobre el dataset real -----------------------------------------

@pytest.mark.skipif(
    not (RUTA_PROCESSED / "sima_diario_modelado.parquet").exists(),
    reason="falta data/processed/sima_diario_modelado.parquet "
           "(corre uv run python src/agregacion_diaria.py)",
)
def test_el_dataset_cuadra_con_el_diario_de_la_limpieza():
    df = pd.read_parquet(RUTA_PROCESSED / "sima_diario_modelado.parquet")
    diario = pd.read_csv(RUTA_PROCESSED / "sima_limpio_diario.csv",
                         parse_dates=["fecha"])

    assert len(df) == len(diario)
    assert not df.duplicated(CLAVE).any()
    assert df["estacion"].nunique() == 15 and df["zona"].nunique() == 7
    assert df["zona"].notna().all() and df["msnm"].notna().all()
    # Las excedencias son nulas exactamente donde el MDA8 lo es (invariante #13).
    assert df["MDA8"].isna().equals(df["excede_anio_5"].isna())
    for r in RESUMENES:
        assert r.salida in df.columns, r.salida
