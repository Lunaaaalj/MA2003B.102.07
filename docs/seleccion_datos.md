# Selección de datos — resumen

Resultado de la issue #12. Define el conjunto de trabajo para #13, #14 y #15.

## Variable objetivo

| | |
| --- | --- |
| Variable | `O3` (ozono troposférico) |
| Métrica | **MDA8** — máximo diario del promedio móvil de 8 h |
| Unidad | ppb |
| Por qué | Es el indicador de la NOM-020-SSA1-2021 |

## Cobertura

| | Decisión | Razón |
| --- | --- | --- |
| Años | **2021–2025** | 2020 se descarta: 7 de 13 estaciones con 89–100 % de faltantes en `O3` |
| Estaciones | **Las 15** | Ninguna supera el umbral de exclusión en 2021–2025 |

## Variables seleccionadas

| Variable | Qué es | Mecanismo |
| --- | --- | --- |
| `O3` | Ozono | **Objetivo** |
| `TOUT` | Temperatura | Acelera la formación fotoquímica |
| `PRS` | Presión | Altas presiones → estancamiento, actúa como tapa |
| `WSR` | Velocidad del viento | Dispersión |
| `WDR` | Dirección del viento | Dispersión |
| `RAINF` | Precipitación | Nubosidad → menos radiación |
| `CO` | Monóxido de carbono | Sustituto de los COV |
| `NO2` | Dióxido de nitrógeno | Precursor: su fotólisis inicia el ciclo |
| `NOX` | NO + NO2 | Precursores |

Identificadoras: `fecha`, `estacion`, `anio`. No se someten al criterio químico — definen la estructura del panel.

## Pendientes de decidir

| Tema | Situación |
| --- | --- |
| `SR` (radiación solar) | **No está en la lista** pese a ser el motor de la formación fotoquímica |
| `RH` (humedad relativa) | **No está en la lista**; actúa por depósito húmedo |
| `NO2` + `NOX` juntas | `NOX = NO + NO2` → dependencia lineal exacta. Hay que quedarse con una de las dos opciones |
| `PM10`, `PM2.5` | El texto describe el mecanismo (pantalla contra la luz solar) pero no declara si entran |
| `SO2` | No se menciona |

## A tomar en cuenta

- **2025 llega solo hasta el 30 de junio.** El invierno cruza el cambio de año, así que la ventana tiene cinco periodos ene–mar pero solo cuatro nov–dic.
- **Hay centinelas `-9999` sin tratar** en `SR`, `RH` y `TOUT`. Son 14 celdas, pero bastan para que `r(O3, SR)` se vea como 0.004 en vez de 0.530. Se limpian en #13.
- **`SR` está corrupta en `NO2` y `NTE`** (medias negativas). No es motivo para excluir esas estaciones: se marcan los valores, no las filas.
- **Los datos vienen en ppb; la norma está en ppm.** Límite de 8 h: 0.065 ppm = 65 ppb.
- **El MDA8 todavía no está calculado.** #12 solo decide la métrica; el cálculo y sus reglas de completitud son de #14.
- **No seleccionar por correlación todavía.** Los datos aún no están limpios.

## Referencias

- Procedimiento completo: [`checklist_seleccion_variables.md`](checklist_seleccion_variables.md)
- Variables y faltantes: [`Diccionario_Sima.md`](Diccionario_Sima.md), [`../data/README.md`](../data/README.md)
- Sección del reporte: [`../reports/secciones/seleccion_datos.tex`](../reports/secciones/seleccion_datos.tex)
