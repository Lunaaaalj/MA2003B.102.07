# Datos

## Estructura

- **`raw/`** — Datos originales tal como los entregó SIMA. **Son inmutables**: no se
  editan, no se sobrescriben, no se limpian aquí.
- **`processed/`** — Generado por el pipeline `importar_datos.py` → `limpieza.py` →
  `notebooks/transformaciones.qmd`. **No se versiona** (está en `.gitignore`), salvo
  una excepción: `sima_transformado_horario.parquet`, el dataset limpio y
  transformado **final**, que sí está commiteado al repo (issue #15) porque es el
  que se linkea en el informe (#17) y no todo el equipo necesita correr Python + R
  solo para leerlo.

## Cómo generar `processed/`

```bash
source venv/bin/activate
pip install -r requirements.txt
python src/importar_datos.py            # ~5 min (el padrón es lo lento) -> sima_horario.parquet
python src/importar_datos.py --solo bd  # solo las bases anuales del SIMA
python src/limpieza.py                  # -> sima_limpio_horario.csv / sima_limpio_diario.csv
quarto render notebooks/transformaciones.qmd  # -> sima_transformado_horario.{csv,parquet}
```

Luego, desde Python o desde R:

```python
from src.importar_datos import cargar_bd
df = cargar_bd()                  # 688,184 × 18
```

```r
source("src/cargar_datos.R")
sima <- cargar_sima()             # mismo dataframe
```

## Qué hay en `raw/`

| Archivo | Contenido |
|---|---|
| `BD 2020.xlsx` … `BD 2025.xlsx` | Mediciones **horarias** del SIMA. Una hoja por estación de monitoreo. |
| `Etiquetas.xlsx` | Catálogos: estaciones, contaminantes, parámetros meteorológicos y banderas de calidad. |
| `INFO INVENTARIO SABANA 2018.xlsx` | Inventario de emisiones 2018 por municipio y categoría de fuente (hojas `NL 2018` y `ZMM 2018`). |
| `Padrón medio ambiente.xlsx` | Padrón vehicular, 1,000,473 registros. |

### Inconsistencias entre los BD anuales

Los seis archivos **no** comparten estructura; el script las resuelve, pero hay que
conocerlas antes de tocar los Excel a mano:

| Año | Cómo se sale del molde |
|---|---|
| 2020 | 13 estaciones (aún no existen `NE3` ni `NO3`). |
| 2021 | 14 estaciones (aparece `NE3`). |
| 2022 | 15 estaciones; `NO3` arranca a media hoja (solo 743 horas de datos ese año). |
| 2023 | 15 estaciones, estructura estándar. |
| 2024 | Las **unidades vienen pegadas al encabezado**: `CO (ppm)`, `PM10 (ug/m3)`, `TOUT (ºC)`. |
| 2025 | La columna de fecha se llama **`date`** (no `Fecha y hora`) y hay una **fila de unidades** debajo del encabezado. Cubre hasta el 30 de junio. |

Además, en todos los años buena parte de los valores están guardados **como texto**
(`'66'`, `'54.23'`), no como número.

## Qué hay en `processed/`

| Archivo | Filas × cols | Qué es | ¿Se versiona? |
|---|---|---|---|
| `sima_horario.parquet` | 688,184 × 18 | Las seis bases anuales consolidadas: `fecha`, `estacion`, `anio` + 15 parámetros. | No |
| `sima_limpio_horario.csv` | — | Salida de la limpieza (#13): outliers marcados, `WDR` descompuesto en `viento_u`/`viento_v`. | No |
| `sima_limpio_diario.csv` | — | Agregado diario de lo anterior. | No |
| `resumen_outliers.csv` | — | Conteo de outliers detectados por parámetro. | No |
| `sima_transformado_horario.parquet` | 574,343 × 30 | **Dataset limpio y transformado final** (#14 + #15): variables escaladas/Box-Cox, `hora`/`mes`/`dia_semana`/`fin_de_semana`/`temporada`, `O3_8h`, `outlier_*`, `llovio`. Es el que se linkea en el informe (#17). | **Sí** |
| `sima_transformado_horario.csv` | 574,343 × 30 | Misma tabla que el parquet, en texto. Pesa ~160 MB (pasa el límite de GitHub) — no se commitea, se regenera si hace falta un CSV. | No |
| `padron_vehicular.parquet` | 1,000,473 × 12 | Padrón vehicular. | No |
| `inventario_nl_2018.parquet` | 2,816 × 17 | Emisiones, todo Nuevo León. | No |
| `inventario_zmm_2018.parquet` | 1,109 × 17 | Emisiones, zona metropolitana de Monterrey. | No |
| `etiquetas_*.csv` | — | Catálogos de `Etiquetas.xlsx` ya tabulados. | No |
| `unidades.csv` | 15 | Parámetro → unidad de medición. | No |

Todos estos archivos están en formato **observaciones × variables** (una fila por
`(fecha, estación)`, una columna por parámetro), que es la forma que piden los
métodos multivariados del curso — no hace falta pivotear ancho/largo en ningún
punto del pipeline.

## Estado de los datos consolidados

Verificado sobre `sima_horario.parquet`: sin fechas nulas, sin `(estación, fecha)`
duplicados, cobertura continua del 2020-01-01 al 2025-06-30.

Los faltantes **siguen ahí a propósito** — limpiarlos es la issue #13:

| | CO | NO | NO2 | NOX | O3 | PM10 | PM2.5 | PRS | RAINF | RH | SO2 | SR | TOUT | WSR | WDR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| % faltante | 13.2 | 17.5 | 18.4 | 17.6 | 15.4 | 4.5 | 24.6 | 5.0 | 4.9 | 10.4 | 15.7 | 3.7 | 6.5 | 7.2 | 8.9 |

> **Ojo con las banderas.** `Etiquetas.xlsx` documenta 23 banderas de calidad
> (`P`, `c`, `z`, `o`, …), pero los archivos entregados **no las traen**: se
> revisaron las 87 hojas de los seis BD y no hay una sola celda con letra de
> bandera, solo números o vacíos. Consecuencia para la limpieza (#13): un dato
> faltante ya no se puede atribuir a su causa (falla eléctrica, calibración,
> apagado). La lectura más razonable —no confirmada con SIMA— es que el filtrado
> por banderas ya se aplicó antes de entregarnos los archivos y lo que vemos son
> los huecos que dejó; conviene confirmarlo con la fuente antes de afirmarlo en
> el reporte. El catálogo se conserva en
> `processed/etiquetas_banderas.csv` porque documenta los criterios de validación
> que SIMA usó, y varios son citables en el reporte.

## Contexto de dominio

- [`docs/Rangos de los parámetros del SIMA.pdf`](../docs/) — rangos válidos por parámetro.
- [`docs/Ubicación de las estaciones de monitoreo.docx`](../docs/) — dónde está cada estación.
