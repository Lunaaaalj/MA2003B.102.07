"""Dataset día-estación con predictores agregados (issue #51).

Toma el horario limpio que produce ``limpieza.py`` (#13) y lo colapsa a **una
fila por día-estación**, que es la unidad en la que están definidas las
indicadoras de excedencia del MDA8 y, por lo tanto, la unidad de modelado del
proyecto: clasificar cada día-estación como excedencia o no del MDA8 a 51 ppb a
partir de los precursores y la meteorología de ese mismo día.

Agregar a día tiene dos efectos, y los dos se buscan: la unidad de observación
coincide con la de la variable objetivo, y se reduce la autocorrelación horaria
que haría que 24 filas del mismo día contaran como 24 observaciones
independientes.

**No es un ``groupby().mean()``.** Cada resumen diario es una decisión física —
el máximo de temperatura, el acumulado de radiación, la media de precursores en
la ventana matutina — y la justificación de cada uno está en ``RESUMENES`` y
queda escrita en ``docs/log_agregacion_diaria.md``.

Este módulo es además el hogar definitivo de tres cosas que vivían como código
de notebook y que el modelado necesita: el catálogo de zonas y elevaciones
(``ZONA``, ``ELEV``, provisionales en ``notebooks/05_estacionalidad_ozono.qmd``)
y el calendario de días de asueto (``marcar_calendario``, provisional en
``notebooks/04_eda_cualitativas.qmd``).

Uso::

    uv run python src/agregacion_diaria.py

Uso como módulo (desde una notebook)::

    import sys; sys.path.insert(0, str(RAIZ))
    from src.agregacion_diaria import ZONA, ELEV, marcar_calendario
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import NamedTuple

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

# Se reutiliza el Log de #13 en vez de duplicarlo, y MIN_VENTANAS_DIA porque la
# regla de completitud de aquí se calibra contra la que ya usa el MDA8.
from src.limpieza import (  # noqa: E402
    MIN_VENTANAS_DIA,
    RUTA_PROCESSED,
    Log,
)

CLAVE = ["estacion", "fecha"]

# =============================================================================
# Catálogos geográficos (promovidos desde notebooks/05_estacionalidad_ozono.qmd)
# =============================================================================

# Las 7 zonas del catálogo oficial del SIMA, docs/Ubicación de las estaciones de
# monitoreo.docx.
#
# La agrupación se fija A PRIORI SOBRE GEOGRAFÍA, y eso es deliberado: derivar
# los grupos del comportamiento del ozono para después usarlos como variable
# explicativa del ozono es circular, y es exactamente la crítica que hundió el
# planteamiento anterior del equipo. Que la partición tenga contenido se
# verifica a posteriori (r = 0.806 entre elevación y tasa de excedencia sobre
# las 15 estaciones, notebooks/05_estacionalidad_ozono.qmd), no se usa para
# construirla.
ZONA = {**{k: "Noroeste" for k in ["NO", "NO2", "NO3"]},
        **{k: "Suroeste" for k in ["SO", "SO2"]},
        **{k: "Noreste"  for k in ["NE", "NE2", "NE3"]},
        **{k: "Sureste"  for k in ["SE", "SE2", "SE3"]},
        **{k: "Norte"    for k in ["NTE", "NTE2"]},
        "CE": "Centro", "SUR": "Sur"}

# Elevación en msnm, del mismo catálogo. Va de la planicie (SE3, 334) al pie de
# la Sierra Madre (NO2, 702).
ELEV = {"SE3": 334, "NE3": 346, "SE2": 387, "NE2": 432, "NE": 474, "SE": 500,
        "NTE": 503, "NTE2": 520, "SUR": 555, "CE": 562, "NO": 568, "NO3": 607,
        "SO2": 636, "SO": 674, "NO2": 702}

# =============================================================================
# Calendario (promovido desde notebooks/04_eda_cualitativas.qmd)
# =============================================================================

# fin_de_semana agrupa sábado y domingo pese a que su actividad vehicular
# difiere, y no separa los días de asueto. tipo_dia los separa en cuatro
# niveles: los días de descanso obligatorio de la LFT art. 74, jueves y viernes
# santo, y el periodo 24-31 de diciembre tienen patrón de tráfico anómalo y
# contaminarían cualquier contraste semanal si quedaran dentro de 'laborable'.
PASCUA = {2021: "2021-04-04", 2022: "2022-04-17", 2023: "2023-04-09",
          2024: "2024-03-31", 2025: "2025-04-20"}

NIVELES_TIPO_DIA = ["laborable", "sabado", "domingo", "festivo"]


def calendario_festivos(anios=range(2021, 2026)) -> set:
    """Días de asueto de 2021-2025: 81 fechas, de las cuales 71 caen dentro
    de la cobertura real del dataset (que termina el 2025-06-30)."""
    fest = set()
    for y in anios:
        fest |= {f"{y}-01-01", f"{y}-05-01", f"{y}-09-16", f"{y}-12-25"}
        for mes, n in [(2, 1), (3, 3), (11, 3)]:      # 1er lun feb, 3er lun mar y nov
            dias = pd.date_range(f"{y}-{mes:02d}-01", periods=31, freq="D")
            lunes = [d for d in dias if d.month == mes and d.weekday() == 0]
            fest.add(str(lunes[n - 1].date()))
        p = pd.Timestamp(PASCUA[y])
        fest |= {str((p - pd.Timedelta(days=k)).date()) for k in (3, 2)}
        fest |= {str(d.date()) for d in pd.date_range(f"{y}-12-24", f"{y}-12-31")}
    fest.add("2024-10-01")     # transmisión del Poder Ejecutivo federal
    return {pd.Timestamp(f) for f in fest}


FESTIVOS = calendario_festivos()


def marcar_calendario(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega ``festivo`` (0/1) y ``tipo_dia`` (4 niveles) a partir de ``fecha``."""
    dw = df["fecha"].dt.dayofweek
    df["festivo"] = df["fecha"].dt.normalize().isin(FESTIVOS).astype(int)
    df["tipo_dia"] = np.select([dw == 5, dw == 6], ["sabado", "domingo"], "laborable")
    df.loc[df.festivo == 1, "tipo_dia"] = "festivo"
    df["tipo_dia"] = pd.Categorical(df.tipo_dia, categories=NIVELES_TIPO_DIA)
    return df


def marcar_temporada(df: pd.DataFrame) -> pd.DataFrame:
    """Reconstruye ``temporada`` con el MISMO corte de ``src/limpieza.py``.

    Se repite el corte en vez de arrastrarlo del horario para no depender del
    orden de las columnas del CSV, pero es literalmente el mismo: definir aquí
    una variante paralela rompería la comparabilidad con todo lo ya reportado.
    """
    df["mes"] = df["fecha"].dt.month
    df["anio"] = df["fecha"].dt.year
    df["temporada"] = pd.cut(df["mes"], bins=[0, 2, 5, 8, 11, 12],
                             labels=["invierno", "primavera", "verano", "otoño",
                                     "invierno"],
                             ordered=False)
    df["fin_de_semana"] = df["fecha"].dt.dayofweek.isin([5, 6]).astype(int)
    return df


# =============================================================================
# Ventanas y regla de completitud
# =============================================================================

VENTANA_DIA = tuple(range(24))

# 06-09 inclusivo en los dos extremos: cuatro horas. Es la carga matutina de
# precursores, la que alimenta el pico fotoquímico vespertino de ozono.
VENTANA_PRECURSORES = (6, 7, 8, 9)

# Ventana diurna para el mínimo de RH y para medir la completitud de SR. Fuera
# de ella la radiación vale 0 por definición y la humedad mide otro fenómeno
# (rocío nocturno, no mezcla vertical).
VENTANA_DIURNA = tuple(range(7, 19))

# La referencia es el criterio que el MDA8 ya usa: 18 de 24 ventanas móviles
# válidas (MIN_VENTANAS_DIA en limpieza.py, documentado en docs/log_limpieza.md).
# Son 3/4 de la ventana, y esa proporción es la que se traslada a las ventanas
# más cortas para no inventar un umbral nuevo por cada una.
MIN_HORAS_DIA = MIN_VENTANAS_DIA                       # 18 de 24
MIN_HORAS_PRECURSORES = 3                              # 3 de 4
MIN_HORAS_DIURNA = 9                                   # 9 de 12


class Resumen(NamedTuple):
    """Un resumen diario: qué se calcula, sobre qué horas, y cuándo es válido."""

    salida: str
    variable: str
    func: str
    ventana: tuple                 # horas sobre las que se calcula
    ventana_completitud: tuple     # horas sobre las que se exige el mínimo
    min_horas: int
    justificacion: str


RESUMENES = [
    Resumen("TOUT_max", "TOUT", "max", VENTANA_DIA, VENTANA_DIA, MIN_HORAS_DIA,
            "Máximo, no media: el motor fotoquímico es el pico térmico del día, "
            "y además alinea la variable con el MDA8, que también es un máximo."),
    Resumen("SR_acum", "SR", "sum", VENTANA_DIA, VENTANA_DIURNA, MIN_HORAS_DIURNA,
            "Acumulado de insolación (kWh/m² sobre el día), no promedio de 24 h: "
            "el promedio queda diluido por las horas de noche, que valen 0 por "
            "definición. Como esas horas aportan 0, la suma sobre el día ES el "
            "acumulado de horas con luz. La completitud sí se mide sobre la "
            "ventana diurna: un día al que le faltan seis horas de tarde pasaría "
            "el 18/24 habiendo perdido la mitad de la energía real."),
    Resumen("NO_06_09", "NO", "mean", VENTANA_PRECURSORES, VENTANA_PRECURSORES,
            MIN_HORAS_PRECURSORES,
            "Media de la ventana matutina: la carga de precursores de 06-09 h es "
            "la que alimenta el pico vespertino de ozono; promediarla sobre 24 h "
            "la mezcla con el mínimo nocturno."),
    Resumen("NO2_06_09", "NO2", "mean", VENTANA_PRECURSORES, VENTANA_PRECURSORES,
            MIN_HORAS_PRECURSORES, "Ídem NO_06_09."),
    Resumen("NOX_06_09", "NOX", "mean", VENTANA_PRECURSORES, VENTANA_PRECURSORES,
            MIN_HORAS_PRECURSORES, "Ídem NO_06_09."),
    Resumen("CO_06_09", "CO", "mean", VENTANA_PRECURSORES, VENTANA_PRECURSORES,
            MIN_HORAS_PRECURSORES,
            "Ídem NO_06_09. CO es además el proxy de COV disponible: el SIMA no "
            "mide compuestos orgánicos volátiles especiados."),
    Resumen("WSR_media", "WSR", "mean", VENTANA_DIA, VENTANA_DIA, MIN_HORAS_DIA,
            "Capacidad de dispersión del día."),
    Resumen("WSR_min", "WSR", "min", VENTANA_DIA, VENTANA_DIA, MIN_HORAS_DIA,
            "Estancamiento. Es una señal distinta de la media, no una redundancia: "
            "un día ventoso con una hora de calma acumula localmente igual que uno "
            "de viento flojo constante, y la media no lo distingue."),
    Resumen("PRS_media", "PRS", "mean", VENTANA_DIA, VENTANA_DIA, MIN_HORAS_DIA,
            "La presión varía poco dentro del día; la media la resume sin pérdida "
            "y es el indicador de sistema anticiclónico (subsidencia, inversión)."),
    Resumen("RH_media", "RH", "mean", VENTANA_DIA, VENTANA_DIA, MIN_HORAS_DIA,
            "Contenido de humedad del día."),
    Resumen("RH_min_diurna", "RH", "min", VENTANA_DIURNA, VENTANA_DIURNA,
            MIN_HORAS_DIURNA,
            "Mínimo DIURNO: marca el desarrollo de la capa de mezcla de la tarde, "
            "que es cuando se forma el ozono. Sobre 24 h el mínimo cae de "
            "madrugada y mide otro fenómeno."),
    Resumen("viento_u_media", "viento_u", "mean", VENTANA_DIA, VENTANA_DIA,
            MIN_HORAS_DIA,
            "Media VECTORIAL del viento (componente este-oeste). Promediar WSR da "
            "magnitud sin transporte neto: un día de viento fuerte que rota 180° "
            "tiene media escalar alta y media vectorial cercana a cero, y es la "
            "segunda la que describe a dónde se fue la masa de aire."),
    Resumen("viento_v_media", "viento_v", "mean", VENTANA_DIA, VENTANA_DIA,
            MIN_HORAS_DIA, "Ídem viento_u_media (componente norte-sur)."),
    Resumen("PM10_media", "PM10", "mean", VENTANA_DIA, VENTANA_DIA, MIN_HORAS_DIA,
            "Carga de partículas del día. Entra como covariable de fuente común, "
            "no como precursor de ozono."),
    Resumen("PM2.5_media", "PM2.5", "mean", VENTANA_DIA, VENTANA_DIA, MIN_HORAS_DIA,
            "Ídem PM10_media."),
    Resumen("SO2_media", "SO2", "mean", VENTANA_DIA, VENTANA_DIA, MIN_HORAS_DIA,
            "Trazador de fuente industrial fija, que distingue el origen de la "
            "carga del de las fuentes móviles que aportan NOx y CO."),
]


def _resumir(df: pd.DataFrame, r: Resumen, idx: pd.MultiIndex,
             cache: dict) -> pd.Series:
    """Aplica un ``Resumen`` y anula los días-estación que no llegan al mínimo."""
    if r.ventana not in cache:
        cache[r.ventana] = df[df["hora"].isin(r.ventana)]
    calculo = cache[r.ventana]

    if r.ventana_completitud not in cache:
        cache[r.ventana_completitud] = df[df["hora"].isin(r.ventana_completitud)]
    completitud = cache[r.ventana_completitud]

    valor = (calculo.groupby(CLAVE, observed=True)[r.variable]
                    .agg(r.func).reindex(idx))
    horas = (completitud.groupby(CLAVE, observed=True)[r.variable]
                        .count().reindex(idx).fillna(0))
    return valor.where(horas >= r.min_horas).rename(r.salida)


def resumir_lluvia(df: pd.DataFrame, idx: pd.MultiIndex) -> pd.Series:
    """``llovio``: 1 si cualquier hora del día registró precipitación.

    La regla de completitud es asimétrica a propósito. Una sola hora con
    ``RAINF > 0`` es evidencia definitiva de que llovió, aunque falten las otras
    23; en cambio afirmar que NO llovió sí exige haber observado el día casi
    completo, porque el aguacero pudo caer justo en las horas ausentes. Por eso
    ``RAINF`` no se interpola en #13 (la lluvia es un proceso discontinuo) y por
    eso aquí un día mayormente vacío y sin lluvia registrada queda NaN, no 0.
    """
    g = df.groupby(CLAVE, observed=True)["RAINF"]
    hubo = g.max().reindex(idx) > 0
    horas = g.count().reindex(idx).fillna(0)
    llovio = pd.Series(np.nan, index=idx, name="llovio")
    llovio[horas >= MIN_HORAS_DIA] = 0.0
    llovio[hubo.fillna(False)] = 1.0
    return llovio


# =============================================================================
# Orquestación
# =============================================================================

def agregar_a_diario(horario: pd.DataFrame, log: Log) -> pd.DataFrame:
    """Colapsa el horario limpio a una fila por día-estación con predictores."""
    log.add("1. Entrada",
            f"Horario limpio (#13): {len(horario):,} filas × {horario.shape[1]} "
            f"columnas, {horario['estacion'].nunique()} estaciones, "
            f"{horario['fecha'].min():%Y-%m-%d} → {horario['fecha'].max():%Y-%m-%d}.")

    df = horario.copy()
    df["fecha"] = df["fecha"].dt.normalize()
    idx = pd.MultiIndex.from_frame(
        df[CLAVE].drop_duplicates().sort_values(CLAVE, kind="stable"))

    log.add("2. Regla de completitud",
            f"Referencia: el criterio del MDA8, {MIN_VENTANAS_DIA} de 24 ventanas "
            f"móviles válidas (docs/log_limpieza.md). Es el 75 % de la ventana, y "
            f"esa proporción se traslada a las ventanas más cortas en vez de "
            f"inventar un umbral por variable.")
    log.add("2. Regla de completitud",
            f"Día completo (24 h): mínimo {MIN_HORAS_DIA} horas válidas. "
            f"Ventana de precursores 06-09 h (4 h): mínimo "
            f"{MIN_HORAS_PRECURSORES}, medido SOBRE LA VENTANA y no sobre las "
            f"24 h. Ventana diurna 07-18 h (12 h): mínimo {MIN_HORAS_DIURNA}.")
    log.add("2. Regla de completitud",
            "Las filas que no llegan al mínimo quedan NaN. No se imputan: la "
            "regresión y el discriminante las descartan listwise, y con 22,529 "
            "días-estación de MDA8 válido hay margen de sobra.")

    cache: dict = {}
    columnas = [_resumir(df, r, idx, cache) for r in RESUMENES]
    columnas.append(resumir_lluvia(df, idx))
    diario = pd.concat(columnas, axis=1).reset_index()

    for r in RESUMENES:
        n = int(diario[r.salida].isna().sum())
        log.add("3. Resúmenes diarios",
                f"`{r.salida}` = {r.func}({r.variable}) sobre "
                f"{_nombre_ventana(r.ventana)}, mínimo {r.min_horas} h válidas en "
                f"{_nombre_ventana(r.ventana_completitud)}. Descarta {n:,} "
                f"días-estación ({n/len(diario)*100:.1f} %). {r.justificacion}")
    n = int(diario["llovio"].isna().sum())
    log.add("3. Resúmenes diarios",
            f"`llovio` = 1 si alguna hora del día tuvo RAINF > 0; 0 si no hubo "
            f"ninguna y hay al menos {MIN_HORAS_DIA} horas válidas; NaN en otro "
            f"caso. Descarta {n:,} días-estación ({n/len(diario)*100:.1f} %). "
            f"Una hora con lluvia es evidencia definitiva; afirmar que no llovió "
            f"exige haber observado el día casi completo.")
    log.add("3. Resúmenes diarios",
            "WDR no se resume: es circular y ya está representada por las "
            "componentes viento_u y viento_v, que sí se pueden promediar.")
    return diario


def agregar_agrupacion(diario: pd.DataFrame, log: Log) -> pd.DataFrame:
    """Añade zona, elevación, calendario y temporada."""
    diario["zona"] = diario["estacion"].map(ZONA)
    diario["msnm"] = diario["estacion"].map(ELEV)
    sin_zona = sorted(diario.loc[diario["zona"].isna(), "estacion"].unique())
    if sin_zona:
        raise ValueError(f"Estaciones fuera del catálogo de zonas: {sin_zona}")

    diario = marcar_temporada(marcar_calendario(diario))

    log.add("4. Variables de agrupación",
            f"zona ({diario['zona'].nunique()} niveles) y msnm, del catálogo "
            f"oficial docs/Ubicación de las estaciones de monitoreo.docx. La "
            f"agrupación se fija a priori sobre geografía: derivarla del "
            f"comportamiento del ozono y luego usarla para explicar ozono sería "
            f"circular.")
    dias_fest = diario.loc[diario["festivo"] == 1, "fecha"].nunique()
    log.add("4. Variables de agrupación",
            f"tipo_dia ({', '.join(NIVELES_TIPO_DIA)}) y festivo, promovidos "
            f"desde notebooks/04_eda_cualitativas.qmd. El calendario genera "
            f"{len(FESTIVOS)} fechas para 2021-2025 completos; dentro de la "
            f"cobertura real del dataset (que termina el 2025-06-30) caen "
            f"{dias_fest} días de asueto, o "
            f"{int(diario['festivo'].sum()):,} filas día-estación.")
    log.add("4. Variables de agrupación",
            "temporada con el mismo corte de src/limpieza.py, no una variante "
            "paralela. Se conservan también mes, anio y fin_de_semana.")
    return diario


def unir_objetivo(diario: pd.DataFrame, objetivo: pd.DataFrame,
                  log: Log) -> pd.DataFrame:
    """Une los predictores al MDA8 y las indicadoras de excedencia (#13)."""
    faltan = set(map(tuple, objetivo[CLAVE].values)) - set(
        map(tuple, diario[CLAVE].values))
    if faltan:
        raise ValueError(f"{len(faltan)} días-estación del diario de #13 sin "
                         f"predictores; las claves no coinciden.")

    n0 = len(objetivo)
    df = objetivo.merge(diario, on=CLAVE, how="left", validate="one_to_one")
    if len(df) != n0:
        raise ValueError(f"El join cambió el número de filas: {n0} → {len(df)}.")

    log.add("5. Unión con la variable objetivo",
            f"Left join contra sima_limpio_diario.csv por (estacion, fecha): "
            f"{len(df):,} filas, las mismas del diario de #13. Trae MDA8, "
            f"ventanas_validas, O3_max_1h y las cuatro indicadoras de excedencia.")
    log.add("5. Unión con la variable objetivo",
            f"MDA8 válido en {int(df['MDA8'].notna().sum()):,} filas "
            f"({df['MDA8'].notna().mean()*100:.1f} %). Excedencias del umbral de "
            f"51 ppb (escenario principal de modelado): "
            f"{int(df['excede_anio_5'].sum()):,} "
            f"({df['excede_anio_5'].mean()*100:.1f} % de los días válidos).")

    completos = df[[r.salida for r in RESUMENES] + ["llovio"]].notna().all(axis=1)
    modelables = int((completos & df["MDA8"].notna()).sum())
    log.add("5. Unión con la variable objetivo",
            f"Filas con MDA8 válido Y los {len(RESUMENES)+1} predictores "
            f"completos: {modelables:,} ({modelables/len(df)*100:.1f} % del "
            f"total). Es el tamaño efectivo de un modelo que descarte listwise.")

    # PM2.5 es el cuello de botella: arrastra el 25 % de faltantes que ya traia
    # del horario (docs/log_limpieza.md) y domina la perdida listwise. Se
    # cuantifica aqui para que #54 y #55 decidan con el numero delante, no de
    # oido: es la unica variable cuya exclusion cambia el tamano de muestra de
    # forma material.
    sin_pm25 = [r.salida for r in RESUMENES if r.salida != "PM2.5_media"]
    n_sin = int((df[sin_pm25 + ["llovio"]].notna().all(axis=1)
                 & df["MDA8"].notna()).sum())
    log.add("5. Unión con la variable objetivo",
            f"PM2.5_media es el cuello de botella: sin ella el conjunto "
            f"listwise sube a {n_sin:,} filas, {n_sin - modelables:,} más "
            f"({(n_sin - modelables)/modelables*100:.0f} %). Es la única "
            f"variable cuya exclusión cambia el tamaño de muestra de forma "
            f"material, y la decisión de conservarla o no corresponde a #54/#55.")
    return df


def _nombre_ventana(v: tuple) -> str:
    if v == VENTANA_DIA:
        return "el día (24 h)"
    if v == VENTANA_PRECURSORES:
        return "06-09 h (4 h)"
    if v == VENTANA_DIURNA:
        return "07-18 h (12 h)"
    return f"{v[0]:02d}-{v[-1]:02d} h"


def construir(horario: pd.DataFrame,
              objetivo: pd.DataFrame) -> tuple[pd.DataFrame, Log]:
    """Pipeline completo: horario limpio + diario de #13 → dataset de modelado."""
    log = Log("Log de agregación diaria (issue #51)")
    diario = agregar_a_diario(horario, log)
    diario = agregar_agrupacion(diario, log)
    df = unir_objetivo(diario, objetivo, log)

    orden = (CLAVE + ["zona", "msnm", "anio", "mes", "temporada", "tipo_dia",
                      "festivo", "fin_de_semana"]
             + [r.salida for r in RESUMENES] + ["llovio"]
             + ["MDA8", "ventanas_validas", "O3_max_1h",
                "excede_anio_1", "excede_anio_3", "excede_anio_5", "excede_1h"])
    df = df[orden].sort_values(CLAVE, kind="stable").reset_index(drop=True)

    log.add("6. Salida",
            f"Dataset día-estación de modelado: {len(df):,} filas × "
            f"{df.shape[1]} columnas ({len(RESUMENES)+1} predictores agregados, "
            f"8 de agrupación y calendario, 7 de la variable objetivo).")
    return df, log


def cargar_entradas() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lee las dos salidas de ``limpieza.py``; falla con instrucción si faltan."""
    horario = RUTA_PROCESSED / "sima_limpio_horario.csv"
    diario = RUTA_PROCESSED / "sima_limpio_diario.csv"
    for ruta in (horario, diario):
        if not ruta.exists():
            raise FileNotFoundError(
                f"Falta {ruta.relative_to(RAIZ)}. data/processed/ no se versiona: "
                f"regenéralo con `uv run python src/limpieza.py`.")
    return (pd.read_csv(horario, parse_dates=["fecha"]),
            pd.read_csv(diario, parse_dates=["fecha"]))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dataset día-estación con predictores agregados (#51)")
    parser.add_argument("--log", default=str(RAIZ / "docs" / "log_agregacion_diaria.md"))
    args = parser.parse_args()

    df, log = construir(*cargar_entradas())

    RUTA_PROCESSED.mkdir(parents=True, exist_ok=True)
    salida = RUTA_PROCESSED / "sima_diario_modelado.parquet"
    df.to_parquet(salida, index=False)
    print(f"\nDataset escrito en {salida}")

    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    Path(args.log).write_text(log.a_markdown(), encoding="utf-8")
    print(f"Log escrito en {args.log}")


if __name__ == "__main__":
    main()
