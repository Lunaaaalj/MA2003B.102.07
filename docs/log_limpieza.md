# Log de limpieza (issue #13)


## 0. Entrada

- Consolidado crudo: 688,184 filas × 18 columnas.

## 1. Selección (#12)

- Años 2021–2025: 574,082 de 688,184 filas (83.4 %). Se descarta 2020 completo (114,102 filas, 16.6 %) por ausencia de O3.
- Variables conservadas: 15 (O3, CO, NO, NO2, NOX, SO2, PM10, PM2.5, TOUT, RH, SR, RAINF, PRS, WSR, WDR). Descartadas: ninguna.
- Estaciones: 15 (se conservan todas; la estación es un identificador espacial, no una magnitud medida).
- Cobertura temporal real: 2021-01-01 00:00:00 → 2025-06-30 23:00:00.

## 2. Duplicados

- Filas idénticas: 0 (0.00 %). Pares (fecha, estación) repetidos: 0 (0.00 %). Eliminadas: 0.
- No hay duplicados que eliminar. Las filas de sobra que aparecen al abrir los .xlsx en Excel son renglones vacíos al final de cada hoja y pandas los descarta en la importación (#9).

## 3. Valores espurios

- (a) Centinelas -9999 → NaN: 14 celdas (0.0002 %). Es el código de dato ausente del datalogger, no una medición.
- (b) Topes de saturación (999/1000/1001 µg/m³) en PM → NaN: 6 celdas (0.0001 %).
- (c) Fuera del rango físico del sensor → NaN: 1339 celdas (0.0155 %). Desglose: O3=1, CO=1, NO=11, NOX=12, PM2.5=1, TOUT=3, RH=276, SR=995, WSR=39.
- (d) Fuera del rango de OPERACIÓN anual, CONSERVADOS y marcados: O3=6 (0.00 %); CO=24 (0.00 %); NO=4 (0.00 %); NOX=4 (0.00 %); SO2=1 (0.00 %); TOUT=63 (0.01 %); SR=94 (0.02 %); RAINF=8 (0.00 %); PRS=7987 (1.39 %); WSR=1655 (0.29 %). No se borran porque el rango de operación es inconsistente entre años (el mínimo de PRS pasa de 687.5 a 700 mmHg y el de TOUT de -6.5 a 0 °C sin justificación física), de modo que aplicarlo al pie de la letra eliminaría mediciones válidas.

## 4. Rejilla horaria

- Horas ausentes insertadas como filas vacías: 261 (0.045 %). Total: 574,343 filas.

## 5. Faltantes

- Método único: interpolación temporal lineal, límite 3 h, sin extrapolar, por estación.
- Celdas imputadas: 144,160 de 8,615,145 (1.67 %).
- Celdas que permanecen NaN: 502,633 (5.83 %). Corresponden a huecos largos (paros prolongados de estación) y NO se imputan.
- RAINF y WDR reciben trato aparte: RAINF no se interpola (proceso discontinuo); WDR se interpola en componentes sin/cos por ser circular.
- Detalle por variable:

```
       faltantes_antes  pct_antes  imputadas  pct_imputadas  faltantes_despues  pct_despues
O3               37252       6.49      12028           2.09              25224         4.39
CO               41321       7.19       5960           1.04              35361         6.16
NO               51263       8.93      14954           2.60              36309         6.32
NO2              47243       8.23      10415           1.81              36828         6.41
NOX              46309       8.06      10594           1.84              35715         6.22
SO2              57632      10.03      19953           3.47              37679         6.56
PM10             22749       3.96       8636           1.50              14113         2.46
PM2.5           142615      24.83      24566           4.28             118049        20.55
TOUT             32557       5.67       5883           1.02              26674         4.64
RH               52364       9.12       6256           1.09              46108         8.03
SR               24502       4.27       4615           0.80              19887         3.46
RAINF            17251       3.00          0           0.00              17251         3.00
PRS              20211       3.52       5940           1.03              14271         2.48
WSR              27310       4.75       7537           1.31              19773         3.44
WDR              26214       4.56       6823           1.19              19391         3.38
```

## 6. Atributos derivados

- viento_u, viento_v: descomposición vectorial de (WSR, WDR). WDR es circular y no puede entrar como número a una correlación, un PCA o una regresión; las componentes sí.
- hora, mes, dia_semana, fin_de_semana, temporada: el ozono tiene ciclo diurno y estacional marcado, y el contraste entre semana/fin de semana es el indicador clásico de la contribución del tráfico.
- MDA8 (máximo diario del promedio móvil de 8 h): 23,931 días-estación, de los cuales 22,529 válidos (94.1 %) con el criterio de completitud de 6/8 horas por ventana y 18/24 ventanas por día.
- Excedencias NOM-020-SSA1-2021 umbral anio_1 (65 ppb): 2,400 días-estación (10.7 % de los días válidos).
- Excedencias NOM-020-SSA1-2021 umbral anio_3 (60 ppb): 3,614 días-estación (16.0 % de los días válidos).
- Excedencias NOM-020-SSA1-2021 umbral anio_5 (51 ppb): 6,917 días-estación (30.7 % de los días válidos).

## 7. Outliers

- Decisión: se detectan, se marcan con una columna indicadora y se CONSERVAN. No se winsorizan ni se eliminan.
- Se excluyen del criterio IQR: WDR, RAINF, SR. WDR es circular y su cuartil carece de sentido (produce un límite inferior de -98°); RAINF tiene 98 % de ceros, así que su IQR vale 0 y marcaría como atípica toda lluvia registrada. Para el viento se usan en su lugar las componentes viento_u y viento_v.
- Razón: el objetivo del proyecto es clasificar excedencias de O3, es decir, los eventos de concentración alta. Recortar la cola superior eliminaría exactamente el fenómeno que se quiere modelar y sesgaría a la baja cualquier estimación de riesgo. Lo mismo aplica a los precursores: un pico de NOX en hora punta es información, no ruido.
- El error de medición ya se removió en el paso 3 por criterio físico, que es verificable, a diferencia del criterio estadístico: en una distribución asimétrica como la de los contaminantes, el IQR marca como atípico un porcentaje alto de observaciones perfectamente reales.
- Detalle por variable:

```
          pct_iqr_1_5  pct_iqr_3  pct_z_mayor_3  limite_inf  limite_sup     max
variable                                                                       
O3               2.51       0.23           1.33      -23.00       73.00  265.00
CO               2.06       0.30           1.05       -0.96        3.50   37.00
NO              11.53       7.13           2.37       -8.75       22.85  500.00
NO2              3.84       0.65           1.53      -12.30       38.90  167.80
NOX              8.36       3.60           2.21      -18.68       60.33  500.00
SO2              6.78       2.99           1.15       -0.95        9.05  404.70
PM10             4.79       1.43           1.56      -23.50      132.50  998.00
PM2.5            3.73       0.81           1.23      -15.11       51.85  782.00
TOUT             0.81       0.00           0.34        3.64       43.24   47.58
RH               0.00       0.00           0.00      -11.00      125.00  100.00
PRS              0.62       0.00           0.20      691.70      739.70  750.00
WSR              1.43       0.39           0.51       -5.65       21.95  179.70
```

## 8. Variables categóricas

- Nominales: estacion (15 niveles), temporada (4 niveles). Binaria: fin_de_semana. Cíclicas codificadas como enteros: hora (0–23), mes (1–12), dia_semana (0–6) — son ordinales cíclicas, no continuas.
- No se generan dummies en el dataset limpio, a propósito: la codificación depende de la técnica y crearlas aquí obligaría a todo el equipo a arrastrar 15 columnas extra sirvan o no.
- Cuándo sí hacen falta: regresión lineal múltiple, regresión multivariada, análisis discriminante y cualquier modelo que resuelva un sistema lineal necesitan dummies con k-1 niveles (una categoría de referencia) para evitar colinealidad perfecta con el intercepto.
- Cuándo no: PCA, análisis factorial y conglomerados operan sobre la matriz de covarianza o de distancias entre variables numéricas; meter dummies binarias infla artificialmente la varianza explicada. En conglomerados, la estación suele usarse para validar el agrupamiento obtenido, no como insumo.
- hora y mes conviene codificarlas como sin/cos (2π·h/24, 2π·m/12) en modelos lineales: como enteros, hacen que las 23:00 queden a 23 unidades de las 00:00 cuando en realidad son consecutivas.

## 9. Salida

- Dataset horario limpio: 574,343 filas × 38 columnas.
- Dataset diario (MDA8 y excedencias): 23,931 filas × 9 columnas.
