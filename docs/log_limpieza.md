# Log de limpieza (issue #13)


## 0. Entrada

- Consolidado crudo: 754,603 filas × 18 columnas.

## 1. Selección (#12)

- Años 2021–2025: 640,501 de 754,603 filas (84.9 %). Se descarta 2020 completo (114,102 filas, 15.1 %) por ausencia de O3.
- Variables conservadas: 15 (O3, CO, NO, NO2, NOX, SO2, PM10, PM2.5, TOUT, RH, SR, RAINF, PRS, WSR, WDR). Descartadas: ninguna.
- Estaciones: 15 (se conservan todas; la estación es un identificador espacial, no una magnitud medida).
- Cobertura temporal real: 2021-01-01 00:00:00 → 2025-12-31 23:00:00.

## 2. Duplicados

- Filas idénticas: 0 (0.00 %). Pares (fecha, estación) repetidos: 0 (0.00 %). Eliminadas: 0.
- No hay duplicados que eliminar. Las filas de sobra que aparecen al abrir los .xlsx en Excel son renglones vacíos al final de cada hoja y pandas los descarta en la importación (#9).

## 3. Valores espurios

- (a) Centinelas -9999 → NaN: 26 celdas (0.0003 %). Es el código de dato ausente del datalogger, no una medición.
- (b) Topes de saturación (999/1000/1001 µg/m³) en PM → NaN: 6 celdas (0.0001 %).
- (c) Fuera del rango físico del sensor → NaN: 1450 celdas (0.0151 %). Desglose: O3=1, CO=1, NO=11, NOX=28, PM2.5=1, TOUT=3, RH=285, SR=1079, PRS=1, WSR=40.
- (d) Fuera del rango de OPERACIÓN anual, CONSERVADOS y marcados: O3=6 (0.00 %); CO=24 (0.00 %); NO=273 (0.04 %); NOX=193 (0.03 %); SO2=1 (0.00 %); TOUT=63 (0.01 %); SR=95 (0.01 %); RAINF=31 (0.00 %); PRS=8070 (1.26 %); WSR=1657 (0.26 %). No se borran porque el rango de operación es inconsistente entre años (el mínimo de PRS pasa de 687.5 a 700 mmHg y el de TOUT de -6.5 a 0 °C sin justificación física), de modo que aplicarlo al pie de la letra eliminaría mediciones válidas.

## 4. Rejilla horaria

- Horas ausentes insertadas como filas vacías: 82 (0.013 %). Total: 640,583 filas.

## 5. Faltantes

- Método único: interpolación temporal lineal, límite 3 h, sin extrapolar, por estación.
- Celdas imputadas: 159,156 de 9,608,745 (1.66 %).
- Celdas que permanecen NaN: 580,265 (6.04 %). Corresponden a huecos largos (paros prolongados de estación) y NO se imputan.
- RAINF y WDR reciben trato aparte: RAINF no se interpola (proceso discontinuo); WDR se interpola en componentes sin/cos por ser circular.
- Detalle por variable:

```
       faltantes_antes  pct_antes  imputadas  pct_imputadas  faltantes_despues  pct_despues
O3               42135       6.58      13153           2.05              28982         4.52
CO               50723       7.92       7216           1.13              43507         6.79
NO               56752       8.86      16561           2.59              40191         6.27
NO2              51837       8.09      11335           1.77              40502         6.32
NOX              52161       8.14      11505           1.80              40656         6.35
SO2              63000       9.83      20798           3.25              42202         6.59
PM10             26399       4.12       9379           1.46              17020         2.66
PM2.5           163212      25.48      28575           4.46             134637        21.02
TOUT             39807       6.21       6385           1.00              33422         5.22
RH               66558      10.39       6813           1.06              59745         9.33
SR               26626       4.16       5183           0.81              21443         3.35
RAINF            19360       3.02          0           0.00              19360         3.02
PRS              23742       3.71       6356           0.99              17386         2.71
WSR              29243       4.57       8483           1.32              20760         3.24
WDR              27866       4.35       7414           1.16              20452         3.19
```

## 6. Atributos derivados

- viento_u, viento_v: descomposición vectorial de (WSR, WDR). WDR es circular y no puede entrar como número a una correlación, un PCA o una regresión; las componentes sí.
- hora, mes, dia_semana, fin_de_semana, temporada: el ozono tiene ciclo diurno y estacional marcado, y el contraste entre semana/fin de semana es el indicador clásico de la contribución del tráfico.
- MDA8 (máximo diario del promedio móvil de 8 h): 26,691 días-estación, de los cuales 25,100 válidos (94.0 %) con el criterio de completitud de 6/8 horas por ventana y 18/24 ventanas por día.
- Excedencias NOM-020-SSA1-2021 umbral anio_1 (65 ppb): 2,825 días-estación (11.3 % de los días válidos).
- Excedencias NOM-020-SSA1-2021 umbral anio_3 (60 ppb): 4,236 días-estación (16.9 % de los días válidos).
- Excedencias NOM-020-SSA1-2021 umbral anio_5 (51 ppb): 8,021 días-estación (32.0 % de los días válidos).

## 7. Outliers

- Decisión: se detectan, se marcan con una columna indicadora y se CONSERVAN. No se winsorizan ni se eliminan.
- Se excluyen del criterio IQR: WDR, RAINF, SR. WDR es circular y su cuartil carece de sentido (produce un límite inferior de -98°); RAINF tiene 98 % de ceros, así que su IQR vale 0 y marcaría como atípica toda lluvia registrada. Para el viento se usan en su lugar las componentes viento_u y viento_v.
- Razón: el objetivo del proyecto es clasificar excedencias de O3, es decir, los eventos de concentración alta. Recortar la cola superior eliminaría exactamente el fenómeno que se quiere modelar y sesgaría a la baja cualquier estimación de riesgo. Lo mismo aplica a los precursores: un pico de NOX en hora punta es información, no ruido.
- El error de medición ya se removió en el paso 3 por criterio físico, que es verificable, a diferencia del criterio estadístico: en una distribución asimétrica como la de los contaminantes, el IQR marca como atípico un porcentaje alto de observaciones perfectamente reales.
- Detalle por variable:

```
          pct_iqr_1_5  pct_iqr_3  pct_z_mayor_3  limite_inf  limite_sup     max
variable                                                                       
O3               2.64       0.23           1.30      -23.00       73.00  265.00
CO               2.20       0.34           1.09       -0.95        3.40   37.00
NO              11.68       7.29           2.06       -8.70       22.50  500.00
NO2              3.82       0.63           1.53      -12.40       38.80  167.80
NOX              8.39       3.64           2.01      -18.65       60.15  500.00
SO2              6.89       3.10           1.18       -0.80        8.80  404.70
PM10             4.78       1.41           1.59      -24.60      129.96  998.00
PM2.5            3.87       0.87           1.26      -14.00       50.00  782.00
TOUT             0.88       0.00           0.36        4.16       43.04   47.58
RH               0.00       0.00           0.00       -8.50      123.50  100.00
PRS              0.64       0.00           0.20      692.20      739.40  750.00
WSR              1.47       0.37           0.50       -5.35       21.45  179.70
```

## 8. Variables categóricas

- Nominales: estacion (15 niveles), temporada (4 niveles). Binaria: fin_de_semana. Cíclicas codificadas como enteros: hora (0–23), mes (1–12), dia_semana (0–6) — son ordinales cíclicas, no continuas.
- No se generan dummies en el dataset limpio, a propósito: la codificación depende de la técnica y crearlas aquí obligaría a todo el equipo a arrastrar 15 columnas extra sirvan o no.
- Cuándo sí hacen falta: regresión lineal múltiple, regresión multivariada, análisis discriminante y cualquier modelo que resuelva un sistema lineal necesitan dummies con k-1 niveles (una categoría de referencia) para evitar colinealidad perfecta con el intercepto.
- Cuándo no: PCA, análisis factorial y conglomerados operan sobre la matriz de covarianza o de distancias entre variables numéricas; meter dummies binarias infla artificialmente la varianza explicada. En conglomerados, la estación suele usarse para validar el agrupamiento obtenido, no como insumo.
- hora y mes conviene codificarlas como sin/cos (2π·h/24, 2π·m/12) en modelos lineales: como enteros, hacen que las 23:00 queden a 23 unidades de las 00:00 cuando en realidad son consecutivas.

## 9. Salida

- Dataset horario limpio: 640,583 filas × 38 columnas.
- Dataset diario (MDA8 y excedencias): 26,691 filas × 9 columnas.
