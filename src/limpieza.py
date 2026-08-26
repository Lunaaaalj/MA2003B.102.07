"""Limpieza del subconjunto seleccionado en la issue #12 (issue #13).

Toma el consolidado crudo que produce ``importar_datos.py`` (#9) y entrega un
dataset limpio, listo para las técnicas multivariadas, junto con un log
cuantificado de cada decisión (necesario para el informe #17).

El orden de las operaciones NO es el de la lista de la issue, y es deliberado:

    1. selección (#12)          
    2. duplicados               
    3. valores espurios → NaN   
    4. rejilla horaria completa 
    5. faltantes               
    6. atributos derivados      
    7. outliers                 
    8. categóricas y dummies

Invertir 3 y 7 haría que ``-9999`` apareciera como outlier extremo y que el
999 de PM2.5 pasara como concentración válida.

Uso::

    python src/limpieza.py                      
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
RUTA_PROCESSED = RAIZ / "data" / "processed"

# =============================================================================
# Parámetros de la selección (issue #12)
# =============================================================================

ANIOS = [2021, 2022, 2023, 2024, 2025]  # 2020 descartado: O3 ausente en 7 de 13 estaciones

OBJETIVO = "O3"

# Precursores y proxies de COV documentados en la revisión de literatura (#12)
CONTAMINANTES = ["CO", "NO", "NO2", "NOX", "SO2", "PM10", "PM2.5"]

# Meteorología con mecanismo documentado sobre la formación de O3
METEOROLOGICAS = ["TOUT", "RH", "SR", "RAINF", "PRS", "WSR", "WDR"]


VARIABLES = [OBJETIVO, *CONTAMINANTES, *METEOROLOGICAS]

# =============================================================================
# Reglas de validez física
# =============================================================================

# Rango del fabricante: es un límite FÍSICO del sensor, estable entre años.
# Se usa como filtro duro porque un valor fuera de aquí no puede ser una
# medición real bajo ninguna circunstancia.
RANGO_FABRICANTE = {
    "O3": (0, 1000), "PM10": (0, 1000), "PM2.5": (0, 1000),
    "NO": (0, 500), "NO2": (0, 500), "NOX": (0, 500), "SO2": (0, 500),
    "CO": (0, 50), "RH": (0, 100), "WSR": (0, 180), "TOUT": (-50, 50),
    "SR": (0, 1.4), "PRS": (449.9, 824.9), "WDR": (0, 360),
    "RAINF": (0, 400)
}

# Rango de operación declarado por SIMA, por año. NO se usa como filtro duro:
# es inconsistente entre años (el mínimo de PRS pasa de 687.5 a 700 mmHg sin
# razón física, y el de TOUT de -6.5 a 0 °C pese a que en Monterrey hiela).
# Se usa solo para CONTAR y REPORTAR sospechosos, no para borrarlos.
RANGO_OPERACION = {
    2020: {"PM10": (0, 800), "PM2.5": (0, 205.94), "O3": (0, 153), "NO": (0, 500), "NO2": (0, 200), "NOX": (0, 500), "SO2": (0, 200), "CO": (0, 20), "RH": (0, 100), "WSR": (0, 75), "TOUT": (0, 41), "SR": (0, 1), "PRS": (690, 750), "WDR": (0, 360), "RAINF": (0, 30)},
    2021: {"PM10": (0, 800), "PM2.5": (0, 325), "O3": (0, 175), "NO": (0, 350), "NO2": (0, 100), "NOX": (0, 400), "SO2": (0, 300), "CO": (0, 10), "RH": (0, 100), "WSR": (0, 40), "TOUT": (-6.5, 45), "SR": (0, 1), "PRS": (690, 740), "WDR": (0, 360), "RAINF": (0, 80)},
    2022: {"PM10": (0, 999), "PM2.5": (0, 450), "O3": (0, 160), "NO": (0, 400), "NO2": (0, 175), "NOX": (0, 420), "SO2": (0, 200), "CO": (0, 8), "RH": (0, 100), "WSR": (0, 35), "TOUT": (-5, 45), "SR": (0, 1.25), "PRS": (700, 740), "WDR": (0, 360), "RAINF": (0, 25)},
    2023: {"PM10": (0, 900), "PM2.5": (0, 800), "O3": (0, 175), "NO": (0, 500), "NO2": (0, 175), "NOX": (0, 500), "SO2": (0, 250), "CO": (0, 14), "RH": (0, 100), "WSR": (0, 40), "TOUT": (0, 45), "SR": (0, 1), "PRS": (690, 740), "WDR": (0, 360), "RAINF": (0, 70)},
    2024: {"PM10": (0, 999), "PM2.5": (0, 999), "O3": (0, 180), "NO": (0, 400), "NO2": (0, 130), "NOX": (0, 500), "SO2": (0, 150), "CO": (0, 18), "RH": (0, 100), "WSR": (0, 38), "TOUT": (-4, 45.5), "SR": (0, 1.26), "PRS": (687.5, 740), "WDR": (0, 360), "RAINF": (0, 50)},
    2025: {"PM10": (0, 820), "PM2.5": (0, 350), "O3": (0, 185), "NO": (0, 350), "NO2": (0, 175), "NOX": (0, 400), "SO2": (0, 405), "CO": (0, 10), "RH": (0, 100), "WSR": (0, 40), "TOUT": (-4.5, 45), "SR": (0, 1.2), "PRS": (688, 740), "WDR": (0, 360), "RAINF": (0, 25)},
}

CENTINELA = -9999

# Valores tope de saturación del equipo de partículas. Un PM2.5 de exactamente
# 999 µg/m3 no es una concentración: es el desbordamiento del registro.
TOPES_PM = {"PM10": [999, 1000, 1001], "PM2.5": [999, 1000, 1001]}

# =============================================================================
# Parámetros de imputación y norma
# =============================================================================

LIMITE_INTERPOLACION = 3

NOM_O3_MDA8 = {"anio_1": 65.0, "anio_3": 60.0, "anio_5": 51.0}
NOM_O3_1H = 90.0

MIN_HORAS_VENTANA = 6
MIN_VENTANAS_DIA = 18


# =============================================================================
# Log
# =============================================================================

class Log:
    """Acumula el registro cuantificado de cada paso (requisito de #13 y #17)."""

    def __init__(self) -> None:
        self.pasos: list[tuple[str, str]] = []

    def add(self, paso: str, detalle: str) -> None:
        self.pasos.append((paso, detalle))
        print(f"[{paso}] {detalle}")

    def a_markdown(self) -> str:
        lineas = ["# Log de limpieza (issue #13)", ""]
        actual = None
        for paso, detalle in self.pasos:
            if paso != actual:
                lineas += ["", f"## {paso}", ""]
                actual = paso
            lineas.append(f"- {detalle}")
        return "\n".join(lineas) + "\n"


# =============================================================================
# Pasos de limpieza
# =============================================================================

def seleccionar(df: pd.DataFrame, log: Log) -> pd.DataFrame:
    """Aplica el recorte decidido en #12: años, variables y estaciones."""
    n0 = len(df)
    df = df[df["anio"].isin(ANIOS)].copy()
    log.add("1. Selección (#12)",
            f"Años {min(ANIOS)}–{max(ANIOS)}: {len(df):,} de {n0:,} filas "
            f"({len(df)/n0*100:.1f} %). Se descarta 2020 completo "
            f"({n0-len(df):,} filas, {(n0-len(df))/n0*100:.1f} %) por ausencia de O3.")

    columnas = ["fecha", "estacion", "anio", *VARIABLES]
    descartadas = [c for c in df.columns if c not in columnas]
    df = df[columnas]
    log.add("1. Selección (#12)",
            f"Variables conservadas: {len(VARIABLES)} ({', '.join(VARIABLES)}). "
            f"Descartadas: {', '.join(descartadas) if descartadas else 'ninguna'}.")
    log.add("1. Selección (#12)",
            f"Estaciones: {df['estacion'].nunique()} (se conservan todas; "
            f"la estación es un identificador espacial, no una magnitud medida).")
    log.add("1. Selección (#12)",
            f"Cobertura temporal real: {df['fecha'].min()} → {df['fecha'].max()}.")
    return df


def quitar_duplicados(df: pd.DataFrame, log: Log) -> pd.DataFrame:
    """Elimina duplicados. En este dataset no hay"""
    n0 = len(df)
    n_exactos = int(df.duplicated().sum())
    n_clave = int(df.duplicated(subset=["fecha", "estacion"]).sum())
    df = df.drop_duplicates(subset=["fecha", "estacion"], keep="first")
    log.add("2. Duplicados",
            f"Filas idénticas: {n_exactos} ({n_exactos/n0*100:.2f} %). "
            f"Pares (fecha, estación) repetidos: {n_clave} ({n_clave/n0*100:.2f} %). "
            f"Eliminadas: {n0-len(df)}.")
    if n_exactos == 0 and n_clave == 0:
        log.add("2. Duplicados",
                "No hay duplicados que eliminar. Las filas de sobra que aparecen "
                "al abrir los .xlsx en Excel son renglones vacíos al final de cada "
                "hoja y pandas los descarta en la importación (#9).")
    return df


def corregir_espurios(df: pd.DataFrame, log: Log) -> pd.DataFrame:
    """Convierte a NaN todo valor que no puede ser una medición real.

      a) centinela -9999 del datalogger
      b) valores tope de saturación en partículas
      c) fuera del rango físico del sensor (rango de fabricante)

    El rango de operación anual NO se aplica como filtro: solo se reporta.
    """
    n_celdas = len(df) * len(VARIABLES)

    # a) centinela -9999 del datalogger
    n_cent = 0
    for v in VARIABLES:
        m = df[v] <= CENTINELA
        n_cent += int(m.sum())
        df.loc[m, v] = np.nan
    log.add("3. Valores espurios",
            f"(a) Centinelas -9999 → NaN: {n_cent} celdas ({n_cent/n_celdas*100:.4f} %). "
            f"Es el código de dato ausente del datalogger, no una medición.")

    # (b) topes de saturación en partículas
    n_tope = 0
    for v, topes in TOPES_PM.items():
        if v in VARIABLES:
            m = df[v].isin(topes)
            n_tope += int(m.sum())
            df.loc[m, v] = np.nan
    log.add("3. Valores espurios",
            f"(b) Topes de saturación (999/1000/1001 µg/m³) en PM → NaN: {n_tope} celdas "
            f"({n_tope/n_celdas*100:.4f} %).")

    # (c) rango de fabricante
    detalle_fab = []
    n_fab = 0
    for v in VARIABLES:
        lo, hi = RANGO_FABRICANTE[v]
        m = df[v].notna() & ((df[v] < lo) | (df[v] > hi))
        k = int(m.sum())
        if k:
            detalle_fab.append(f"{v}={k}")
            n_fab += k
        df.loc[m, v] = np.nan
    log.add("3. Valores espurios",
            f"(c) Fuera del rango físico del sensor → NaN: {n_fab} celdas "
            f"({n_fab/n_celdas*100:.4f} %). Desglose: "
            f"{', '.join(detalle_fab) if detalle_fab else 'ninguna'}.")

    # (d) reporte del rango de operación anual
    reporte = []
    for v in VARIABLES:
        k = 0
        for anio, rangos in RANGO_OPERACION.items():
            if anio not in ANIOS:
                continue
            lo, hi = rangos[v]
            s = df.loc[df["anio"] == anio, v]
            k += int((s.notna() & ((s < lo) | (s > hi))).sum())
        if k:
            reporte.append(f"{v}={k} ({k/len(df)*100:.2f} %)")
    log.add("3. Valores espurios",
            f"(d) Fuera del rango de OPERACIÓN anual, CONSERVADOS y marcados: "
            f"{'; '.join(reporte) if reporte else 'ninguno'}. "
            f"No se borran porque el rango de operación es inconsistente entre años "
            f"(el mínimo de PRS pasa de 687.5 a 700 mmHg y el de TOUT de -6.5 a 0 °C "
            f"sin justificación física), de modo que aplicarlo al pie de la letra "
            f"eliminaría mediciones válidas.")
    return df


def completar_rejilla(df: pd.DataFrame, log: Log) -> pd.DataFrame:
    """Reindexa cada estación contra su rejilla horaria continua.

    Sin este paso, una interpolación temporal asumiría que dos filas contiguas
    están separadas por una hora aunque falte la marca de tiempo intermedia.
    """
    n0 = len(df)
    partes = []
    for est, sub in df.groupby("estacion", observed=True):
        sub = sub.set_index("fecha").sort_index()
        rejilla = pd.date_range(sub.index.min(), sub.index.max(), freq="h")
        sub = sub.reindex(rejilla)
        sub["estacion"] = est
        sub["anio"] = sub.index.year
        sub.index.name = "fecha"
        partes.append(sub.reset_index())
    df = pd.concat(partes, ignore_index=True)
    log.add("4. Rejilla horaria",
            f"Horas ausentes insertadas como filas vacías: {len(df)-n0} "
            f"({(len(df)-n0)/len(df)*100:.3f} %). Total: {len(df):,} filas.")
    return df


def _interpolar_direccion(sub: pd.DataFrame) -> pd.DataFrame:
    """Interpola WDR en el plano, no en grados.

    Interpolar grados directamente produce errores graves: entre 350° y 10°
    (12° de diferencia real) el promedio aritmético da 180°, exactamente la
    dirección opuesta. Se pasa a componentes, se interpola, y se regresa.
    """
    rad = np.deg2rad(sub["WDR"])
    u, v = np.sin(rad), np.cos(rad)
    u = u.interpolate(method="time", limit=LIMITE_INTERPOLACION, limit_area="inside")
    v = v.interpolate(method="time", limit=LIMITE_INTERPOLACION, limit_area="inside")
    ang = np.rad2deg(np.arctan2(u, v)) % 360
    sub["WDR"] = ang.where(sub["WDR"].isna() & ang.notna(), sub["WDR"])
    return sub


def imputar(df: pd.DataFrame, log: Log) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Interpolación temporal lineal para huecos cortos; el resto queda NaN.

    Justificación del método y del límite de 3 horas:

    - Todas las variables son series horarias fuertemente autocorrelacionadas.
      La media o la mediana global ignoran hora del día y estación del año, y
      aplicarlas a O3 —cuyo ciclo diurno va de ~5 ppb de madrugada a ~60 ppb
      por la tarde— destruiría precisamente el patrón que el proyecto modela.
    - Los faltantes NO son aleatorios (MCAR): cada celda vacía corresponde a una
      hora que SIMA invalidó por calibración, falla eléctrica o condición
      anómala, según el sistema de banderas de Etiquetas.xlsx. Bajo un mecanismo
      MAR, la interpolación local es defendible y la imputación por media global
      no lo es.
    - El límite de 3 h acota el error: un hueco de 1–3 horas se cruza sin salir
      del mismo régimen diurno. Rellenar huecos de días o meses fabricaría la
      variable dependiente.
    - ``limit_area="inside"`` impide extrapolar: no se inventan valores antes de
      la primera medición ni después de la última de cada estación.

    RAINF se excluye: la lluvia es un proceso discontinuo. Interpolar entre dos
    horas secas y una lluviosa inventaría precipitación que no ocurrió.
    """
    continuas = [v for v in VARIABLES if v not in ("WDR", "RAINF")]
    antes = df[VARIABLES].isna().sum()

    partes = []
    for _, sub in df.groupby("estacion", observed=True):
        sub = sub.set_index("fecha").sort_index()
        for v in continuas:
            sub[v] = sub[v].interpolate(
                method="time", limit=LIMITE_INTERPOLACION, limit_area="inside")
        if "WDR" in VARIABLES:
            sub = _interpolar_direccion(sub)
        partes.append(sub.reset_index())
    df = pd.concat(partes, ignore_index=True)

    despues = df[VARIABLES].isna().sum()
    n_celdas = len(df) * len(VARIABLES)
    imputadas = (antes - despues)

    resumen = pd.DataFrame({
        "faltantes_antes": antes,
        "pct_antes": (antes / len(df) * 100).round(2),
        "imputadas": imputadas,
        "pct_imputadas": (imputadas / len(df) * 100).round(2),
        "faltantes_despues": despues,
        "pct_despues": (despues / len(df) * 100).round(2),
    })

    log.add("5. Faltantes",
            f"Método único: interpolación temporal lineal, límite {LIMITE_INTERPOLACION} h, "
            f"sin extrapolar, por estación.")
    log.add("5. Faltantes",
            f"Celdas imputadas: {int(imputadas.sum()):,} de {n_celdas:,} "
            f"({imputadas.sum()/n_celdas*100:.2f} %).")
    log.add("5. Faltantes",
            f"Celdas que permanecen NaN: {int(despues.sum()):,} "
            f"({despues.sum()/n_celdas*100:.2f} %). Corresponden a huecos largos "
            f"(paros prolongados de estación) y NO se imputan.")
    log.add("5. Faltantes",
            f"RAINF y WDR reciben trato aparte: RAINF no se interpola (proceso "
            f"discontinuo); WDR se interpola en componentes sin/cos por ser circular.")
    log.add("5. Faltantes", "Detalle por variable:\n\n```\n" + resumen.to_string() + "\n```")
    return df, resumen


def derivar(df: pd.DataFrame, log: Log) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Construye los atributos derivados: MDA8, viento vectorial y temporales."""
    # --- componentes de viento -------------------------------------------
    if "WSR" in VARIABLES and "WDR" in VARIABLES:
        rad = np.deg2rad(df["WDR"])
        df["viento_u"] = -df["WSR"] * np.sin(rad)
        df["viento_v"] = -df["WSR"] * np.cos(rad)
        log.add("6. Atributos derivados",
                "viento_u, viento_v: descomposición vectorial de (WSR, WDR). "
                "WDR es circular y no puede entrar como número a una correlación, "
                "un PCA o una regresión; las componentes sí.")

    # --- temporales -------------------------------------------------------
    df["hora"] = df["fecha"].dt.hour
    df["mes"] = df["fecha"].dt.month
    df["dia_semana"] = df["fecha"].dt.dayofweek
    df["fin_de_semana"] = (df["dia_semana"] >= 5).astype(int)
    df["temporada"] = pd.cut(df["mes"], bins=[0, 2, 5, 8, 11, 12],
                             labels=["invierno", "primavera", "verano", "otoño", "invierno"],
                             ordered=False)
    log.add("6. Atributos derivados",
            "hora, mes, dia_semana, fin_de_semana, temporada: el ozono tiene ciclo "
            "diurno y estacional marcado, y el contraste entre semana/fin de semana "
            "es el indicador clásico de la contribución del tráfico.")

    # --- MDA8: la variable objetivo normativa -----------------------------
    partes = []
    for _, sub in df.groupby("estacion", observed=True):
        sub = sub.set_index("fecha").sort_index()
        sub["O3_8h"] = sub["O3"].rolling(8, min_periods=MIN_HORAS_VENTANA).mean()
        partes.append(sub.reset_index())
    df = pd.concat(partes, ignore_index=True)

    diario = (df.groupby(["estacion", df["fecha"].dt.date], observed=True)
                .agg(MDA8=("O3_8h", "max"),
                     ventanas_validas=("O3_8h", "count"),
                     O3_max_1h=("O3", "max"))
                .reset_index()
                .rename(columns={"level_1": "dia"}))
    n_dias = len(diario)
    diario.loc[diario["ventanas_validas"] < MIN_VENTANAS_DIA, "MDA8"] = np.nan
    n_invalidos = int(diario["MDA8"].isna().sum())

    for nombre, umbral in NOM_O3_MDA8.items():
        diario[f"excede_{nombre}"] = (diario["MDA8"] > umbral).astype("Int64")
    diario.loc[diario["MDA8"].isna(),
               [f"excede_{n}" for n in NOM_O3_MDA8]] = pd.NA
    diario["excede_1h"] = (diario["O3_max_1h"] > NOM_O3_1H).astype("Int64")

    log.add("6. Atributos derivados",
            f"MDA8 (máximo diario del promedio móvil de 8 h): {n_dias:,} días-estación, "
            f"de los cuales {n_dias-n_invalidos:,} válidos "
            f"({(n_dias-n_invalidos)/n_dias*100:.1f} %) con el criterio de completitud "
            f"de {MIN_HORAS_VENTANA}/8 horas por ventana y {MIN_VENTANAS_DIA}/24 ventanas por día.")
    for nombre, umbral in NOM_O3_MDA8.items():
        k = int(diario[f"excede_{nombre}"].sum())
        log.add("6. Atributos derivados",
                f"Excedencias NOM-020-SSA1-2021 umbral {nombre} ({umbral:.0f} ppb): "
                f"{k:,} días-estación ({k/(n_dias-n_invalidos)*100:.1f} % de los días válidos).")
    return df, diario


# Variables a las que el IQR no aplica:
#   WDR es circular — su cuartil no tiene sentido (el "límite inferior" da -98°).
#   RAINF es de cero inflado (98 % de ceros) — su IQR vale 0, de modo que toda
#   lluvia registrada quedaría marcada como atípica.
SIN_IQR = ["WDR", "RAINF", "SR"]


def analizar_outliers(df: pd.DataFrame, log: Log) -> pd.DataFrame:
    """Detecta outliers y los CONSERVA marcados. Justificación en el log."""
    evaluables = [v for v in VARIABLES if v not in SIN_IQR]
    filas = []
    for v in evaluables:
        s = df[v].dropna()
        q1, q3 = s.quantile([0.25, 0.75])
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        lo3, hi3 = q1 - 3 * iqr, q3 + 3 * iqr
        z = ((s - s.mean()) / s.std()).abs()
        filas.append(dict(
            variable=v,
            pct_iqr_1_5=round(((s < lo) | (s > hi)).mean() * 100, 2),
            pct_iqr_3=round(((s < lo3) | (s > hi3)).mean() * 100, 2),
            pct_z_mayor_3=round((z > 3).mean() * 100, 2),
            limite_inf=round(lo, 2), limite_sup=round(hi, 2), max=round(s.max(), 2),
        ))
    tabla = pd.DataFrame(filas).set_index("variable")

    for v in evaluables:
        s = df[v]
        q1, q3 = s.quantile([0.25, 0.75])
        iqr = q3 - q1
        df[f"outlier_{v}"] = ((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).astype("Int64")

    log.add("7. Outliers",
            "Decisión: se detectan, se marcan con una columna indicadora y se "
            "CONSERVAN. No se winsorizan ni se eliminan.")
    log.add("7. Outliers",
            f"Se excluyen del criterio IQR: {', '.join(SIN_IQR)}. WDR es circular "
            f"y su cuartil carece de sentido (produce un límite inferior de -98°); "
            f"RAINF tiene 98 % de ceros, así que su IQR vale 0 y marcaría como "
            f"atípica toda lluvia registrada. Para el viento se usan en su lugar "
            f"las componentes viento_u y viento_v.")
    log.add("7. Outliers",
            "Razón: el objetivo del proyecto es clasificar excedencias de O3, es "
            "decir, los eventos de concentración alta. Recortar la cola superior "
            "eliminaría exactamente el fenómeno que se quiere modelar y sesgaría a "
            "la baja cualquier estimación de riesgo. Lo mismo aplica a los "
            "precursores: un pico de NOX en hora punta es información, no ruido.")
    log.add("7. Outliers",
            "El error de medición ya se removió en el paso 3 por criterio físico, "
            "que es verificable, a diferencia del criterio estadístico: en una "
            "distribución asimétrica como la de los contaminantes, el IQR marca "
            "como atípico un porcentaje alto de observaciones perfectamente reales.")
    log.add("7. Outliers", "Detalle por variable:\n\n```\n" + tabla.to_string() + "\n```")
    return tabla


def documentar_categoricas(df: pd.DataFrame, log: Log) -> None:
    """Identifica las categóricas y documenta cuándo se necesitan dummies."""
    log.add("8. Variables categóricas",
            f"Nominales: estacion ({df['estacion'].nunique()} niveles), "
            f"temporada (4 niveles). Binaria: fin_de_semana. "
            f"Cíclicas codificadas como enteros: hora (0–23), mes (1–12), "
            f"dia_semana (0–6) — son ordinales cíclicas, no continuas.")
    log.add("8. Variables categóricas",
            "No se generan dummies en el dataset limpio, a propósito: la "
            "codificación depende de la técnica y crearlas aquí obligaría a todo "
            "el equipo a arrastrar 15 columnas extra sirvan o no.")
    log.add("8. Variables categóricas",
            "Cuándo sí hacen falta: regresión lineal múltiple, regresión "
            "multivariada, análisis discriminante y cualquier modelo que resuelva "
            "un sistema lineal necesitan dummies con k-1 niveles (una categoría de "
            "referencia) para evitar colinealidad perfecta con el intercepto.")
    log.add("8. Variables categóricas",
            "Cuándo no: PCA, análisis factorial y conglomerados operan sobre la "
            "matriz de covarianza o de distancias entre variables numéricas; meter "
            "dummies binarias infla artificialmente la varianza explicada. En "
            "conglomerados, la estación suele usarse para validar el agrupamiento "
            "obtenido, no como insumo.")
    log.add("8. Variables categóricas",
            "hora y mes conviene codificarlas como sin/cos (2π·h/24, 2π·m/12) en "
            "modelos lineales: como enteros, hacen que las 23:00 queden a 23 "
            "unidades de las 00:00 cuando en realidad son consecutivas.")


# =============================================================================
# Orquestación
# =============================================================================

def limpiar(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Log]:
    """Ejecuta el pipeline completo y devuelve (horario, diario, outliers, log)."""
    log = Log()
    log.add("0. Entrada", f"Consolidado crudo: {len(df):,} filas × {df.shape[1]} columnas.")
    df = seleccionar(df, log)
    df = quitar_duplicados(df, log)
    df = corregir_espurios(df, log)
    df = completar_rejilla(df, log)
    df, _ = imputar(df, log)
    df, diario = derivar(df, log)
    outliers = analizar_outliers(df, log)
    documentar_categoricas(df, log)

    df["estacion"] = df["estacion"].astype("category")
    df = df.sort_values(["estacion", "fecha"]).reset_index(drop=True)
    log.add("9. Salida",
            f"Dataset horario limpio: {len(df):,} filas × {df.shape[1]} columnas.")
    log.add("9. Salida",
            f"Dataset diario (MDA8 y excedencias): {len(diario):,} filas × "
            f"{diario.shape[1]} columnas.")
    return df, diario, outliers, log


def cargar_consolidado() -> pd.DataFrame:
    """Lee el consolidado de #9; regenera desde los Excel si no existe."""
    parquet = RUTA_PROCESSED / "sima_horario.parquet"
    if parquet.exists():
        return pd.read_parquet(parquet)
    from importar_datos import cargar_bd
    return cargar_bd()


def main() -> None:
    parser = argparse.ArgumentParser(description="Limpieza del dataset SIMA (#13)")
    parser.add_argument("--log", default=str(RAIZ / "docs" / "log_limpieza.md"))
    args = parser.parse_args()

    df, diario, outliers, log = limpiar(cargar_consolidado())

    RUTA_PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(RUTA_PROCESSED / "sima_limpio_horario.csv", index=False)
    diario.to_csv(RUTA_PROCESSED / "sima_limpio_diario.csv", index=False)
    outliers.to_csv(RUTA_PROCESSED / "resumen_outliers.csv")

    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    Path(args.log).write_text(log.a_markdown(), encoding="utf-8")
    print(f"\nLog escrito en {args.log}")


if __name__ == "__main__":
    main()