"""Importación y consolidación de las bases de datos crudas del SIMA (issue #9).

Este módulo es el punto de partida de la Parte II: deja los datos de
``data/raw/`` en un formato único y reproducible dentro de ``data/processed/``,
**sin limpiarlos todavía** (eso es la issue #13). Aquí solo se resuelven las
inconsistencias estructurales entre archivos.

Uso como script (reconstruye todo ``data/processed/``)::

    source venv/bin/activate
    python src/importar_datos.py            # solo genera lo que falte
    python src/importar_datos.py --forzar   # regenera todo desde cero
    python src/importar_datos.py --solo bd  # solo las bases anuales

Uso como módulo (desde un notebook o desde otro script)::

    from src.importar_datos import cargar_bd, cargar_etiquetas

    df = cargar_bd()                 # 2020-2025 consolidado
    df = cargar_bd(anios=[2024, 2025])
"""

from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

import pandas as pd

# --- Rutas -------------------------------------------------------------------
# Se resuelven a partir de la ubicación de este archivo y no del directorio de
# trabajo, para que el script funcione igual desde la raíz del repo, desde
# src/ o desde un notebook en notebooks/.
RAIZ = Path(__file__).resolve().parent.parent
RUTA_RAW = RAIZ / "data" / "raw"
RUTA_PROCESSED = RAIZ / "data" / "processed"

ANIOS = [2020, 2021, 2022, 2023, 2024, 2025]

# --- Esquema canónico de las bases anuales -----------------------------------
# Nombres tal como los define Etiquetas.xlsx. El orden importa: es el orden en
# que quedan las columnas del dataframe consolidado.
PARAMETROS = [
    "CO", "NO", "NO2", "NOX", "O3", "PM10", "PM2.5",     # contaminantes criterio
    "PRS", "RAINF", "RH", "SO2", "SR", "TOUT", "WSR", "WDR",  # meteorología
]
COLUMNAS_BD = ["fecha", "estacion", "anio", *PARAMETROS]

# Esquema real del inventario de emisiones (columnas A:Q de cada hoja).
COLUMNAS_INVENTARIO = [
    "F_emi", "Nom_Edo", "CVE_Edo", "CV_ZM", "Nom_ZM", "CVE_Mun", "Nom_Mun",
    "CAT", "SUB_CAT",
    "E_PM10", "E_PM2.5", "E_SO2", "E_CO", "E_NOX", "E_COV", "E_NH3",
    "Jurisdicción",
]

# Unidad de cada parámetro, según Etiquetas.xlsx (tablas 2 y 3).
UNIDADES = {
    "CO": "ppm", "NO": "ppb", "NO2": "ppb", "NOX": "ppb", "O3": "ppb",
    "PM10": "ug/m3", "PM2.5": "ug/m3", "SO2": "ppb",
    "PRS": "mmHg", "RAINF": "mm/h", "RH": "%", "SR": "kW/m2",
    "TOUT": "C", "WSR": "km/h", "WDR": "grados azimutales",
}


def _normalizar_encabezado(nombre: object) -> str:
    """Lleva un encabezado crudo al nombre canónico del esquema.

    Resuelve las tres formas en que los archivos nombran lo mismo:

    >>> _normalizar_encabezado("Fecha y hora")   # 2020-2024
    'fecha'
    >>> _normalizar_encabezado("date")           # 2025
    'fecha'
    >>> _normalizar_encabezado("CO (ppm)")       # 2024 trae la unidad pegada
    'CO'
    """
    texto = str(nombre).strip()
    texto = re.sub(r"\s*\(.*?\)\s*$", "", texto)  # quita "(ppm)", "(ug/m3)", ...
    sin_acentos = "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    )
    if sin_acentos.lower() in {"fecha y hora", "date", "fecha"}:
        return "fecha"
    # PM2.5 aparece como "PM2.5" y a veces como "PM25"
    canonico = texto.upper().replace(" ", "")
    if canonico in {"PM25", "PM2.5"}:
        return "PM2.5"
    return canonico


def _es_fila_de_unidades(fila: pd.Series) -> bool:
    """¿Esta fila es el renglón de unidades que trae BD 2025 bajo el encabezado?

    La reconoce por su firma: la fecha viene vacía y el resto son textos
    ('ppm', 'ppb', 'mmHg'...) que no se pueden convertir a número.
    """
    if pd.notna(fila.get("fecha")):
        return False
    valores = fila.drop(labels=["fecha"], errors="ignore").dropna()
    if valores.empty:
        return False
    return all(isinstance(v, str) and not _es_numero(v) for v in valores)


def _es_numero(valor: object) -> bool:
    try:
        float(valor)
    except (TypeError, ValueError):
        return False
    return True


def cargar_bd_anio(anio: int) -> pd.DataFrame:
    """Carga un archivo ``BD <anio>.xlsx`` completo en formato largo por estación.

    Cada hoja del libro es una estación de monitoreo, así que se leen todas y
    el nombre de la hoja se promueve a la columna ``estacion``.
    """
    archivo = RUTA_RAW / f"BD {anio}.xlsx"
    if not archivo.exists():
        raise FileNotFoundError(f"No se encontró {archivo}")

    hojas = pd.read_excel(archivo, sheet_name=None, engine="openpyxl")

    marcos = []
    for estacion, hoja in hojas.items():
        hoja = hoja.rename(columns=_normalizar_encabezado)
        # Columnas del esquema que sí trae esta hoja (por si algún año pierde una)
        hoja = hoja.loc[:, [c for c in ["fecha", *PARAMETROS] if c in hoja.columns]]
        hoja = hoja[~hoja.apply(_es_fila_de_unidades, axis=1)]

        hoja["fecha"] = pd.to_datetime(hoja["fecha"], errors="coerce")
        for parametro in PARAMETROS:
            if parametro in hoja.columns:
                # Los Excel guardan varios valores como texto ('66', '54.23');
                # errors="coerce" manda a NaN lo que no sea numérico.
                hoja[parametro] = pd.to_numeric(hoja[parametro], errors="coerce")

        hoja.insert(1, "estacion", estacion.strip().upper())
        marcos.append(hoja)

    df = pd.concat(marcos, ignore_index=True)
    df["anio"] = anio
    # reindex garantiza el mismo esquema aunque un año no traiga algún parámetro
    return df.reindex(columns=COLUMNAS_BD)


def cargar_bd(anios: list[int] | None = None) -> pd.DataFrame:
    """Consolida las bases anuales 2020-2025 en un solo dataframe.

    Resultado: una fila por (fecha, estación) y una columna por parámetro, que
    es la forma que piden los métodos multivariados (observaciones × variables).
    """
    anios = anios or ANIOS
    df = pd.concat([cargar_bd_anio(a) for a in anios], ignore_index=True)
    df["estacion"] = df["estacion"].astype("category")
    return df.sort_values(["estacion", "fecha"], kind="stable").reset_index(drop=True)


def cargar_etiquetas() -> dict[str, pd.DataFrame]:
    """Lee ``Etiquetas.xlsx``: catálogos de estaciones, variables y banderas.

    La hoja *Variables* no es tabular: son cuatro tablas apiladas, cada una
    precedida por un título "Tabla N. ...". Se recorre fila por fila usando el
    último título visto para saber a qué catálogo pertenece cada bloque.
    """
    archivo = RUTA_RAW / "Etiquetas.xlsx"
    crudo = pd.read_excel(archivo, sheet_name="Variables", header=None, engine="openpyxl")

    # El orden importa: el título de las banderas dice "...banderas de
    # contaminantes y parámetros meteorológicos", así que contiene también las
    # agujas de los otros dos bloques. Se busca de lo específico a lo general.
    claves = [
        ("banderas", "banderas"),
        ("estaciones", "estaciones de monitoreo"),
        ("contaminantes", "contaminante criterio"),
        ("meteorologicos", "parametros meteorologicos"),
    ]

    tablas: dict[str, list[list]] = {}
    encabezados: dict[str, list[str]] = {}
    actual: str | None = None

    for _, fila in crudo.iterrows():
        celdas = [c for c in fila.tolist() if pd.notna(c)]
        if not celdas:
            continue
        primera = str(celdas[0]).strip()
        plano = "".join(
            c for c in unicodedata.normalize("NFD", primera.lower())
            if unicodedata.category(c) != "Mn"
        )

        if plano.startswith("tabla"):  # título: abre un bloque nuevo
            actual = next((k for k, aguja in claves if aguja in plano), None)
            continue
        if actual is None:
            continue
        if primera in {"Abreviatura", "Flag"}:  # encabezado del bloque
            encabezados[actual] = [str(c).strip() for c in celdas]
            tablas[actual] = []
            continue
        if actual in tablas and len(celdas) > 1:
            tablas[actual].append([str(c).strip() for c in celdas])

    catalogos = {}
    for nombre, filas in tablas.items():
        cols = encabezados[nombre]
        # Algunas filas traen una nota extra en una columna de más; se recortan
        # o se rellenan para que todas tengan el ancho del encabezado.
        filas = [(f + [None] * len(cols))[: len(cols)] for f in filas]
        catalogos[nombre] = pd.DataFrame(filas, columns=cols)

    # La hoja "Banderas" es la misma tabla ya en formato limpio: se prefiere esa.
    catalogos["banderas"] = pd.read_excel(
        archivo, sheet_name="Banderas", engine="openpyxl"
    ).dropna(how="all")

    return catalogos


def cargar_inventario() -> dict[str, pd.DataFrame]:
    """Lee ``INFO INVENTARIO SABANA 2018.xlsx`` (emisiones por municipio).

    Solo se toman las hojas ``NL 2018`` (todo Nuevo León) y ``ZMM 2018`` (zona
    metropolitana de Monterrey). Las hojas ``Sheet1`` y ``Hoja1`` son residuos
    de tablas dinámicas de quien armó el archivo, no fuentes de datos.
    """
    archivo = RUTA_RAW / "INFO INVENTARIO SABANA 2018.xlsx"
    hojas = {"nl_2018": "NL 2018", "zmm_2018": "ZMM 2018"}
    tablas = {}
    for clave, hoja in hojas.items():
        # A:Q es la tabla real. A la derecha de la Q ambas hojas traen tablas
        # dinámicas pegadas ("Suma de E_PM10", "Etiquetas de fila", columnas
        # sin nombre); si se leen, contaminan de texto columnas numéricas.
        tabla = pd.read_excel(archivo, sheet_name=hoja, usecols="A:Q", engine="openpyxl")
        faltantes = set(COLUMNAS_INVENTARIO) - set(tabla.columns)
        if faltantes:
            raise ValueError(f"{hoja}: cambió el esquema, faltan {sorted(faltantes)}")
        tablas[clave] = tabla.loc[:, COLUMNAS_INVENTARIO].dropna(how="all")
    return tablas


def cargar_padron() -> pd.DataFrame:
    """Lee ``Padrón medio ambiente.xlsx`` (padrón vehicular, ~1 millón de filas).

    Es el archivo más pesado del proyecto (60 MB) y tarda varios minutos en
    leerse desde Excel. Por eso conviene usar siempre la versión en Parquet que
    genera ``construir_processed()``.
    """
    df = pd.read_excel(
        RUTA_RAW / "Padrón medio ambiente.xlsx", sheet_name="Padron", engine="openpyxl"
    )
    df.columns = [str(c).strip().lower() for c in df.columns]
    numericas = {"cantidad", "cilindros", "modelo", "peso"}
    for columna in df.columns:
        if columna in numericas:
            df[columna] = pd.to_numeric(df[columna], errors="coerce")
        else:
            # astype(str) ANTES de category: columnas como 'tipo' mezclan texto
            # y números (' 200 CGI SC' junto a 200) y una categoría de tipos
            # mixtos no se puede serializar a Parquet.
            df[columna] = df[columna].astype("string").str.strip().astype("category")
    return df


def catalogo_unidades() -> pd.DataFrame:
    """Tabla auxiliar parámetro → unidad, para etiquetar ejes y tablas."""
    return pd.DataFrame(
        {"parametro": list(UNIDADES), "unidad": list(UNIDADES.values())}
    )


# --- Construcción de data/processed/ -----------------------------------------

def construir_processed(solo: str = "todo", forzar: bool = False) -> None:
    """Genera los Parquet de ``data/processed/`` a partir de ``data/raw/``."""
    RUTA_PROCESSED.mkdir(parents=True, exist_ok=True)

    def _pendiente(nombre: str) -> Path | None:
        destino = RUTA_PROCESSED / nombre
        if destino.exists() and not forzar:
            print(f"  = {nombre} ya existe (usa --forzar para regenerarlo)")
            return None
        return destino

    if solo in {"todo", "bd"}:
        destino = _pendiente("sima_horario.parquet")
        if destino:
            print("  · leyendo BD 2020-2025 ...")
            df = cargar_bd()
            df.to_parquet(destino, index=False)
            print(f"  ✓ {destino.name}: {len(df):,} filas × {df.shape[1]} columnas")
            catalogo_unidades().to_csv(RUTA_PROCESSED / "unidades.csv", index=False)

    if solo in {"todo", "etiquetas"}:
        for nombre, tabla in cargar_etiquetas().items():
            destino = RUTA_PROCESSED / f"etiquetas_{nombre}.csv"
            if destino.exists() and not forzar:
                print(f"  = {destino.name} ya existe")
                continue
            tabla.to_csv(destino, index=False)
            print(f"  ✓ {destino.name}: {len(tabla)} filas")

    if solo in {"todo", "inventario"}:
        for clave, tabla in cargar_inventario().items():
            destino = _pendiente(f"inventario_{clave}.parquet")
            if destino:
                tabla.to_parquet(destino, index=False)
                print(f"  ✓ {destino.name}: {len(tabla):,} filas × {tabla.shape[1]} col")

    if solo in {"todo", "padron"}:
        destino = _pendiente("padron_vehicular.parquet")
        if destino:
            print("  · leyendo el padrón vehicular (60 MB, tarda unos minutos) ...")
            df = cargar_padron()
            df.to_parquet(destino, index=False)
            print(f"  ✓ {destino.name}: {len(df):,} filas × {df.shape[1]} columnas")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--solo",
        default="todo",
        choices=["todo", "bd", "etiquetas", "inventario", "padron"],
        help="qué fuente construir (por defecto: todo)",
    )
    parser.add_argument(
        "--forzar", action="store_true", help="regenerar aunque el archivo ya exista"
    )
    args = parser.parse_args()

    print(f"raw       : {RUTA_RAW}")
    print(f"processed : {RUTA_PROCESSED}")
    construir_processed(solo=args.solo, forzar=args.forzar)


if __name__ == "__main__":
    main()
