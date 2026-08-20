# [](https://)[](https://)Diccionario de datos — Red de monitoreo [](https://)SIMA (2020–2025)

## 1. Dimensión del dataset


| Concepto                       | Valor                                              |
| ------------------------------ | -------------------------------------------------- |
| Registros (filas)              | **754,603**                                        |
| Columnas                       | **18** (3 identificadoras + 15 parámetros medidos) |
| Estaciones de monitoreo        | 15                                                 |
| Cobertura temporal             | 2020-01-01 00:00 → 2025-12-31 23:00                |
| Granularidad                   | Horaria (una fila = una estación × una hora)       |
| Registros duplicados           | **0**                                              |
| Celdas faltantes en parámetros | 1,188,343 de 11,319,045 →**10.50 %**               |

**Estructura de origen.** Cada libro anual contiene una hoja por estación (13 en 2020, 14 en 2021, 15 de 2022 en adelante), con formato ancho: una fila por hora y una columna por parámetro. La consolidación promueve el nombre de la hoja a la columna `estacion` y apila los seis años.

---

## 2. Diccionario de variables

### 2.1 Variables identificadoras


| Nombre     | Descripción                                                         | Tipo                                   | Valores posibles                                                      | % nulos |
| ---------- | ------------------------------------------------------------------- | -------------------------------------- | --------------------------------------------------------------------- | ------- |
| `fecha`    | Marca temporal de la observación (fecha y hora, resolución horaria) | Fecha/hora (`datetime64`)              | 2020-01-01 00:00 → 2025-12-31 23:00                                   | 0.00    |
| `estacion` | Estación de monitoreo que registró la observación                   | Categórica (nominal, 15 niveles)       | CE, NE, NE2, NE3, NO, NO2, NO3, NTE, NTE2, SE, SE2, SE3, SO, SO2, SUR | 0.00    |
| `anio`     | Año calendario; deriva del archivo de origen                        | Numérica discreta / categórica ordinal | 2020, 2021, 2022, 2023, 2024, 2025                                    | 0.00    |

### 2.2 Contaminantes criterio

Todas son numéricas continuas. El rango de operación es el declarado por SIMA para el año más restrictivo y el más permisivo del periodo; varía año con año (ver §5.3).


| Nombre  | Descripción                                | Unidad | Rango de operación (min–max según año) | Rango observado | Mediana | % nulos |
| ------- | ------------------------------------------ | ------ | -------------------------------------- | --------------- | ------- | ------- |
| `CO`    | Monóxido de carbono                        | ppm    | 0–8 a 0–20                             | 0.0 – 37.0      | 1.17    | 13.31   |
| `NO`    | Monóxido de nitrógeno                      | ppb    | 0–350 a 0–500                          | 0.3 – 945.1     | 5.00    | 16.75   |
| `NO2`   | Dióxido de nitrógeno                       | ppb    | 0–100 a 0–200                          | 0.0 – 188.6     | 11.40   | 17.37   |
| `NOX`   | Óxidos de nitrógeno (suma NO + NO₂)        | ppb    | 0–400 a 0–500                          | −9999 – 971.8   | 17.30   | 16.82   |
| `O3`    | **Ozono** — variable objetivo del proyecto | ppb    | 0–153 a 0–185                          | 0.5 – 265.0     | 23.00   | 14.73   |
| `PM10`  | Material particulado < 10 µm               | µg/m³  | 0–800 a 0–999                          | 1.0 – 1001.0    | 49.00   | 4.63    |
| `PM2.5` | Material particulado < 2.5 µm              | µg/m³  | 0–205.94 a 0–999                       | 0.0 – 999.0     | 17.00   | 25.23   |
| `SO2`   | Dióxido de azufre                          | ppb    | 0–150 a 0–405                          | 0.0 – 404.7     | 3.80    | 15.03   |

*Nota de conversión (Etiquetas.xlsx):* O₃, SO₂ y NO₂ pueden pasarse a ppm dividiendo entre 1000.

### 2.3 Parámetros meteorológicos


| Nombre  | Descripción                       | Unidad            | Rango de operación (min–max según año) | Rango observado | Mediana | % nulos |
| ------- | --------------------------------- | ----------------- | -------------------------------------- | --------------- | ------- | ------- |
| `TOUT`  | Temperatura ambiente              | °C                | −6.5–45 a 0–45.5                       | −9999 – 785.0   | 24.02   | 6.95    |
| `RH`    | Humedad relativa                  | %                 | 0–100                                  | −9999 – 725.0   | 59.00   | 11.38   |
| `SR`    | Radiación solar                   | kW/m²             | 0–1 a 0–1.26                           | −9999 – 604.0   | 0.00    | 3.66    |
| `RAINF` | Precipitación                     | mm/h              | 0–25 a 0–80                            | −9999 – 360.0   | 0.00    | 4.74    |
| `PRS`   | Presión atmosférica (barométrica) | mmHg              | 687.5–750 (según año)                  | 0.0 – 750.0     | 714.40  | 5.08    |
| `WSR`   | Velocidad del viento              | km/h              | 0–35 a 0–75                            | −9999 – 337.0   | 7.40    | 6.87    |
| `WDR`   | Dirección del viento              | grados azimutales | 0–360                                  | −9999 – 360.0   | 116.00  | 8.35    |

**`WDR` es un caso especial:** aunque se almacena como número, es una variable **circular**, no continua — 0° y 360° son la misma dirección (norte). No puede promediarse, escalarse ni correlacionarse como las demás; requiere descomponerse en componentes `sin(θ)` y `cos(θ)`, o bien en las componentes de viento `u = −WSR·sin(θ)` y `v = −WSR·cos(θ)`. Es un atributo derivado a construir en la etapa de transformación.

**`RAINF` y `SR` son de cero inflado:** 98.4 % de los registros válidos de precipitación y 39.6 % de los de radiación solar valen exactamente 0 (noche y días sin lluvia). Son ceros legítimos, no faltantes ni errores, pero rompen los supuestos de normalidad y distorsionan cualquier estandarización.

---

## 3. Catálogo de estaciones

Descripción según `Etiquetas.xlsx`, tabla 1. La cobertura se calculó sobre el consolidado.


| Clave  | Nombre           | Sitio          | Municipio                | Cobertura         | Horas  |
| ------ | ---------------- | -------------- | ------------------------ | ----------------- | ------ |
| `CE`   | Centro           | Obispado       | Monterrey                | 2020–2025         | 52,605 |
| `NE`   | Noreste          | San Nicolás    | San Nicolás de los Garza | 2020–2025         | 52,595 |
| `NE2`  | Noreste 2        | Apodaca        | Apodaca                  | 2020–2025         | 52,593 |
| `NE3`  | *No documentada* | —              | —                        | **2021–2025**     | 43,817 |
| `NO`   | Noroeste         | San Bernabé    | Monterrey                | 2020–2025         | 52,597 |
| `NO2`  | Noroeste 2       | García         | García                   | 2020–2025         | 52,594 |
| `NO3`  | *No documentada* | —              | —                        | **dic 2022–2025** | 27,045 |
| `NTE`  | Norte            | Escobedo       | Escobedo                 | 2020–2025         | 52,595 |
| `NTE2` | Norte 2          | Universidad    | (no indicado)            | 2020–2025         | 52,593 |
| `SE`   | Sureste          | La Pastora     | Guadalupe                | 2020–2025         | 52,599 |
| `SE2`  | Sureste 2        | Juárez         | Juárez                   | 2020–2025         | 52,595 |
| `SE3`  | Sureste 3        | Cadereyta      | (no indicado)            | 2020–2025         | 52,593 |
| `SO`   | Suroeste         | Santa Catarina | Santa Catarina           | 2020–2025         | 52,597 |
| `SO2`  | Suroeste 2       | San Pedro      | San Pedro Garza García   | 2020–2025         | 52,593 |
| `SUR`  | Sur              | Pueblo Serena  | (no indicado)            | 2020–2025         | 52,592 |

---

## 4. Banderas de calidad (`Etiquetas.xlsx`)

SIMA documenta un sistema de banderas que marca el motivo por el que una hora se invalida. **Estas banderas no vienen en los archivos `BD *.xlsx`**: los libros entregados solo traen el valor numérico o la celda vacía. Es decir, ya llegan filtrados — cada celda vacía es una hora que SIMA invalidó por alguna de estas causas, pero el motivo no es recuperable.


| Bandera   | Causa                                               | Hora              |
| --------- | --------------------------------------------------- | ----------------- |
| `P` / `p` | Falla eléctrica                                     | Válida / Inválida |
| `C` / `c` | Calibración                                         | Válida / Inválida |
| `D` / `d` | Apagado                                             | Válida / Inválida |
| `B` / `b` | Malas condiciones                                   | Válida / Inválida |
| `m`       | Positivo sobre el rango                             | Inválida          |
| `l`       | Negativo sobre el rango / ajuste de radiación solar | Inválida          |
| `z`       | Ceros y negativos                                   | Inválida          |
| `o`       | PM10 mayor a 900 µg/m³                              | Inválida          |
| `s`       | Valores repetidos / iguales consecutivos            | Inválida          |
| `r`       | Comparativo PM10 vs PM2.5                           | Inválida          |
| `e`       | Eliminar datos NO y NOx                             | Inválida          |
| `a`       | Eliminar PM < 5 µg/m³ y CO < 0.05 ppm               | Inválida          |
| `f`       | Valor 3× mayor que el anterior (PM10)               | Inválida          |
| `h`       | Salto > 10 °C o > 10 mmHg respecto a la hora previa | Inválida          |
| `n`       | Falla de comunicación                               | Inválida          |
| `x`       | Valor que pasó protocolos pero no debe estar        | Inválida          |
| `u`       | Sin documentar                                      | Sin documentar    |

**Consecuencia metodológica:** los faltantes de este dataset **no son aleatorios (no son MCAR)**. Se concentran donde hubo calibración, falla o condición anómala, lo que los acerca a un mecanismo MAR. Eso condiciona qué imputación es defendible en la issue #13 y debe declararse como supuesto en el informe.

---

## 5. Calidad de los datos: anomalías detectadas

### 5.1 Faltantes


| Variable | % nulo |     | Variable | % nulo |
| -------- | ------ | --- | -------- | ------ |
| `PM2.5`  | 25.23  |     | `RH`     | 11.38  |
| `NO2`    | 17.37  |     | `WDR`    | 8.35   |
| `NOX`    | 16.82  |     | `TOUT`   | 6.95   |
| `NO`     | 16.75  |     | `WSR`    | 6.87   |
| `SO2`    | 15.03  |     | `PRS`    | 5.08   |
| `O3`     | 14.73  |     | `RAINF`  | 4.74   |
| `CO`     | 13.31  |     | `PM10`   | 4.63   |
|          |        |     | `SR`     | 3.66   |

El faltante no está repartido de forma pareja. Para O₃, **2020 es prácticamente inservible**: NTE y SUR tienen 100 %, SE2 100 %, NE 99.9 %, NO 98.4 %, NTE2 93.3 % y NE2 89.1 % de ozono faltante ese año. De 2022 en adelante el faltante de O₃ baja a 1–8 % en casi toda la red (la excepción es NO3, con 30.3 % en 2025).

**% de O₃ faltante por estación y año:**


| Estación | 2020  | 2021 | 2022 | 2023 | 2024 | 2025 |
| -------- | ----- | ---- | ---- | ---- | ---- | ---- |
| CE       | 16.5  | 12.2 | 3.6  | 4.1  | 4.2  | 3.4  |
| NE       | 99.9  | 16.0 | 3.8  | 5.0  | 3.7  | 10.1 |
| NE2      | 89.1  | 18.6 | 3.3  | 7.8  | 7.0  | 6.0  |
| NE3      | —     | 4.9  | 4.4  | 4.2  | 5.2  | 7.6  |
| NO       | 98.4  | 20.3 | 6.2  | 6.0  | 11.0 | 7.4  |
| NO2      | 20.3  | 5.9  | 2.4  | 2.7  | 3.8  | 4.7  |
| NO3      | —     | —    | 5.1  | 16.5 | 3.5  | 30.3 |
| NTE      | 100.0 | 18.5 | 4.3  | 7.3  | 4.0  | 4.2  |
| NTE2     | 93.3  | 9.5  | 2.5  | 2.9  | 5.9  | 4.6  |
| SE       | 7.3   | 5.6  | 2.7  | 2.8  | 2.8  | 3.0  |
| SE2      | 100.0 | 39.3 | 5.5  | 1.6  | 12.0 | 10.0 |
| SE3      | 28.5  | 5.9  | 1.8  | 4.7  | 1.4  | 0.5  |
| SO       | 31.0  | 7.0  | 5.4  | 4.3  | 5.9  | 4.7  |
| SO2      | 3.0   | 2.5  | 2.6  | 1.9  | 1.4  | 1.4  |
| SUR      | 100.0 | 16.4 | 2.6  | 2.8  | 0.9  | 0.9  |

### 5.2 Valores centinela y físicamente imposibles


| Anomalía                    | Variables afectadas                | n    | Interpretación                                                                                                                                  |
| --------------------------- | ---------------------------------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `−9999`                     | NOX, RAINF, RH, SR, TOUT, WSR, WDR | 26   | Código de faltante del datalogger,**no un dato**. Debe volverse `NaN` antes de cualquier cálculo.                                               |
| `RH > 100 %`                | RH                                 | 285  | Imposible por definición (máximos de 714 y 725 %).                                                                                              |
| `TOUT > 50 °C`              | TOUT                               | 3    | Fuera del rango del sensor (−50 a 50 °C); máximo observado 785 °C.                                                                              |
| `SR` en escala equivocada   | SR                                 | ~30  | Valores de 64, 501 y 604 frente a un máximo físico de 1.4 kW/m²: son lecturas en W/m² mezcladas (÷1000).                                        |
| `SR` entre 1.5 y 7.8        | SR                                 | ~730 | Exceden el rango de fabricante; concentradas en NTE (493) y SO (172), lo que sugiere falla o descalibración de sensor, no evento meteorológico. |
| `WSR > 100 km/h`            | WSR                                | 418  | Supera cualquier viento registrado en la ZMM; 306 de ellos en 2021.                                                                             |
| `PRS = 0` o `PRS < 500`     | PRS                                | 2    | Presión atmosférica nula es imposible.                                                                                                          |
| `PM10 ≥ 999`, `PM2.5 = 999` | PM10, PM2.5                        | 6    | Valores tope (999, 1000, 1001) característicos de saturación o centinela, no concentraciones reales.                                            |
| `CO > 18 ppm`               | CO                                 | 24   | Excede el rango de operación de todos los años; máximo 37 ppm.                                                                                  |

### 5.3 Los rangos de operación no son estables entre años

El PDF de rangos define límites **distintos para cada año**, y algunos son más estrictos que los datos reales. El caso crítico es `PRS`: el rango declarado para 2022 es 700–740 mmHg, y con ese criterio **6,305 registros de ese año** (≈ 4.8 %) quedarían fuera, cuando en 2021, 2023, 2024 y 2025 el mismo tipo de lectura sí es válida porque el límite inferior baja a 687–690. Aplicar el PDF literalmente borraría datos legítimos.

Lo mismo ocurre con `TOUT`, cuyo mínimo declarado es 0 °C en 2020 y 2023 pero −6.5 °C en 2021: en Monterrey hay heladas reales, así que el límite de 0 °C es un error de captura del documento, no una regla física.

**Criterio recomendado para #13:** usar el **rango de fabricante** (que sí es físico y estable) como filtro duro para eliminar imposibles, y tratar el rango de operación anual como señal de sospecha a revisar, no como regla de borrado automático.


| Parámetro         | Rango de fabricante |
| ----------------- | ------------------- |
| PM10, PM2.5, O3   | 0 – 1000            |
| NO, NO2, NOx, SO2 | 0 – 500             |
| CO                | 0 – 50              |
| RH                | 0 – 100             |
| WS (WSR)          | 0 – 180             |
| TEMP (TOUT)       | −50 – 50            |
| SR                | 0 – 1.4             |
| BP (PRS)          | 449.9 – 824.9       |
| WD (WDR)          | 0 – 360             |

### 5.4 Rejilla temporal incompleta

Ninguna estación tiene la serie horaria completa: faltan entre 3 (CE) y 16 (SUR) marcas de tiempo respecto a la rejilla horaria continua de su periodo. Son huecos de hora, no filas vacías: la fila simplemente no existe. Cualquier interpolación temporal exige reindexar contra una rejilla horaria completa primero, o el método asumirá que dos observaciones contiguas están separadas por una hora cuando no lo están.
