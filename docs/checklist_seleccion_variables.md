# Checklist — Selección del conjunto de datos

Procedimiento para decidir **qué subconjunto de los datos del SIMA entra al
análisis**: qué años, qué estaciones, qué columnas y cuál es la variable objetivo.

- **Issue:** #12 (Selección del conjunto de datos a utilizar)
- **Depende de:** #4 (objetivo), #10 (diccionario), #11 (calidad de datos)
- **Define el alcance de:** #13, #14, #15
- **Entregable:** `docs/seleccion_datos.md` (este archivo es el *procedimiento*,
  no el entregable)

> **Alcance.** Este checklist decide *qué se usa*. No limpia, no transforma y no
> modela: todo eso vive en las issues posteriores — ver
> [Fuera de alcance](#fuera-de-alcance).

---

## Principio rector

Las decisiones de esta issue deben apoyarse en criterios que **no requieran datos
ya limpios**: el objetivo de investigación, la disponibilidad de cada variable y la
definición de las variables entre sí.

> ⚠️ **No seleccionar variables por correlación en esta etapa.** Los datos crudos
> contienen centinelas `-9999` y valores imposibles que todavía no se tratan (#13).
> Medido sobre `sima_horario.parquet`: **11 valores** de `-9999` en `SR` —el
> 0.0017 % de sus mediciones— hacen que `r(O3, SR)` se vea como **0.004**. Tratados
> esos 11 valores, la correlación real es **0.530**. Un criterio del tipo «descartar
> si |r| < 0.2» habría eliminado una de las variables más informativas del dataset.
> El tamizado estadístico corresponde a #14, con los datos ya limpios.

---

## Fase 1 — Variable objetivo

- [X]  **Confirmar la variable objetivo:** `O3` (ozono troposférico), según el
  objetivo de investigación definido en #4.
- [X]  **Elegir la métrica** con que se representa: `O3` horario crudo o el
  **máximo diario del promedio móvil de 8 h (MDA8)**. Ver
  [Anexo A](#anexo-a--variable-objetivo-o3-horario-o-mda8).
- [X]  **Fijar la unidad de observación** que se deriva de esa métrica:
  ¿(estación, hora)? ¿(estación, día)? ¿promedio de la ZMM?
- [X]  Dejar la decisión y su justificación normativa escritas en el entregable.

> Esta elección determina la unidad de observación de todo lo que sigue, así que
> va primero.

---

## Fase 2 — Cobertura: años y estaciones

- [X]  **Decidir años incluidos/excluidos**, con la tabla de inconsistencias de
  [`data/README.md`](../data/README.md):


| Año  | Consideración                                                                  |
| ---- | ------------------------------------------------------------------------------ |
| 2020 | 13 estaciones; no existen`NE3` ni `NO3`                                        |
| 2021 | 14 estaciones; aparece`NE3`                                                    |
| 2022 | 15 estaciones;`NO3` solo tiene 743 horas                                       |
| 2023 | 15 estaciones, estructura estándar                                             |
| 2024 | 15 estaciones, estructura estándar                                             |
| 2025 | Cubre solo hasta el 30 de junio →**sesgo estacional** si se mezcla sin control |

- [X]  **Decidir estaciones incluidas/excluidas.** Registro de `O3` por estación,
  medido sobre `sima_horario.parquet`:


| Estación | Filas      | % faltante en`O3` |
| -------- | ---------- | ----------------- |
| `SO2`    | 48 178     | 2.24              |
| `SE`     | 48 183     | 4.15              |
| `NE3`    | 39 378     | 5.56              |
| `NO2`    | 48 179     | 7.09              |
| `CE`     | 48 190     | 7.69              |
| `SE3`    | 48 178     | 7.74              |
| `NO3`    | **22 606** | 8.53              |
| `SO`     | 48 041     | 10.32             |
| `NTE2`   | 48 178     | 20.93             |
| `SUR`    | 48 176     | 22.38             |
| `NE2`    | 48 177     | 23.70             |
| `NTE`    | 48 180     | 24.77             |
| `NE`     | 48 180     | 25.12             |
| `NO`     | 48 181     | 26.38             |
| `SE2`    | 48 179     | 29.18             |

- [X]  Fijar una **regla explícita** de exclusión (p. ej. «se excluye toda estación
  con > 30 % faltante en la variable objetivo dentro de los años elegidos»).
- [X]  Verificar ubicación y entorno de las estaciones que se conserven, con
  `docs/Ubicación de las estaciones de monitoreo.docx`.

> ⚠️ Excluir años y excluir estaciones interactúan: si se descartan 2020 y 2021,
> `NE3` y `NO3` dejan de ser un problema de panel desbalanceado. Decidir años primero.

---

## Fase 3 — Columnas

Las 15 variables medidas más las 3 identificadoras. Para cada una, decidir
**incluir / excluir** con uno de los cuatro criterios de abajo.

- [X]  **Congelar la lista de candidatas a priori:**


| Bloque                         | Variables                                        | Papel                |
| ------------------------------ | ------------------------------------------------ | -------------------- |
| Objetivo                       | `O3`                                             | Variable a explicar  |
| Meteorológicas                 | `TOUT`, `RH`, `SR`, `WSR`, `WDR`, `PRS`, `RAINF` | Foco del objetivo    |
| Precursores / co-contaminantes | `NO`, `NO2`, `NOX`, `CO`, `SO2`, `PM10`, `PM2.5` | Control y contexto   |
| Identificadoras                | `fecha`, `estacion`, `anio`                      | Estructura del panel |

### Criterios de decisión

- [ ]  **C1 · Relevancia respecto al objetivo.** El objetivo (#4) es explicar el `O3`
  a partir de **factores meteorológicos**. Las meteorológicas entran por
  definición. Para cada contaminante hay que decidir si entra como precursor
  (justificación química: `NOx` y COV forman ozono) o si se descarta por no
  aportar al objetivo.
- [ ]  **C2 · Disponibilidad.** Porcentaje de faltantes por parámetro
  (fuente: [`data/README.md`](../data/README.md)):


| CO   | NO   | NO2  | NOX  | O3   | PM10 | PM2.5 | PRS | RAINF | RH   | SO2  | SR  | TOUT | WSR | WDR |
| ---- | ---- | ---- | ---- | ---- | ---- | ----- | --- | ----- | ---- | ---- | --- | ---- | --- | --- |
| 13.2 | 17.5 | 18.4 | 17.6 | 15.4 | 4.5  | 24.6  | 5.0 | 4.9   | 10.4 | 15.7 | 3.7 | 6.5  | 7.2 | 8.9 |

Fijar un umbral y justificarlo. `PM2.5` (24.6 %) es la candidata obvia a discusión.

- [ ]  **C3 · Redundancia por definición.** `NOX ≈ NO + NO2` por definición química:
  las tres son linealmente dependientes. **Decidir cuál se conserva** —`NOX`
  agregado o el par `NO`+`NO2` desagregado— y documentar la razón. Es una
  decisión estructural que se toma aquí, no un hallazgo empírico posterior.
- [ ]  **C4 · Papel en la tabla.** `fecha`, `estacion` y `anio` son **identificadores**,
  no parámetros medidos: definen la estructura del panel y no compiten con las
  demás en la selección. Van en la lista de cobertura (Fase 2), no en la de
  variables.
- [ ]  Producir la **lista final**: cada variable incluida con su criterio, cada
  variable excluida con el criterio que la eliminó.

---

## Fase 4 — Entregable

- [ ]  Escribir `docs/seleccion_datos.md` con **cinco listas explícitas**:
  1. Años/archivos **incluidos**
  2. Años/archivos **excluidos** + razón
  3. Estaciones **incluidas/excluidas** + razón
  4. **Variables seleccionadas**, cada una con su criterio (C1–C4)
  5. **Variables descartadas**, cada una con el criterio que la eliminó
- [ ]  Declarar explícitamente la **variable objetivo** y su métrica.
- [ ]  Comentar el resumen en la issue #12.
- [ ]  Actualizar el alcance de #13, #14 y #15 con lo decidido aquí.

---

## Fuera de alcance

Se registran aquí para que no se pierdan y para dejar claro dónde van.


| Tema                                                                     | Issue     | Por qué no va en #12                                    |
| ------------------------------------------------------------------------ | --------- | ------------------------------------------------------- |
| Aplicar rangos válidos del PDF del SIMA; tratar centinelas`-9999`        | #13       | Es limpieza                                             |
| Imputación de faltantes;*listwise* vs. *pairwise*                        | #13       | Es limpieza                                             |
| Transformar`WDR` a `sin`/`cos`; `log(x+1)` en variables asimétricas      | #14       | Es transformación                                       |
| Calcular el MDA8                                                         | #14       | #12 solo**decide** la métrica; calcularla es otra issue |
| Matrices de correlación (Pearson/Spearman), mapas de calor               | #14       | Requiere datos limpios                                  |
| Varianza casi nula, asimetría, tamizado univariado                       | #14       | Requiere datos limpios                                  |
| Multicolinealidad: determinante, número de condición, VIF, KMO, Bartlett | #14 / #15 | Es diagnóstico de modelo                                |
| Distancia de Mahalanobis, outliers multivariados                         | #15       | Es análisis                                             |
| PCA, dendrogramas de variables                                           | #15       | Es análisis                                             |
| Selección por modelo:`regsubsets`, LASSO, validación cruzada             | #15       | Es modelado                                             |
| Estratificación por estación, centrado dentro de grupo                   | #15       | Es diseño de análisis                                   |

---

## Anexo A — Variable objetivo: `O3` horario o MDA8

**MDA8** = *Maximum Daily 8-hour Average*: promedio móvil de 8 h sobre las
concentraciones horarias, y de esos promedios se toma el máximo del día. Produce un
valor por estación y por día.

Es la métrica normativa. La **NOM-020-SSA1-2021** (DOF 28-oct-2021) fija el límite de
ozono sobre el promedio móvil de ocho horas, evaluado como el máximo de los máximos
diarios:


| Fuente            | Indicador                          | Valor                     | En ppb       |
| ----------------- | ---------------------------------- | ------------------------- | ------------ |
| NOM-020-SSA1-2021 | Promedio móvil 8 h (Año 1 / 3 / 5) | 0.065 / 0.060 / 0.051 ppm | 65 / 60 / 51 |
| NOM-020-SSA1-2021 | 1 hora                             | 0.090 ppm                 | 90           |
| OMS AQG 2021      | MDA8, percentil 99                 | 100 µg/m³                 | ≈ 51         |

> La NOM evalúa contra el **máximo**; la OMS contra el **percentil 99**.

### Comparación


|                                   | MDA8 diario                 | `O3` horario      |
| --------------------------------- | --------------------------- | ----------------- |
| Unidad de observación             | (estación, día)             | (estación, hora)  |
| n aproximado                      | ~30 000                     | 688 184           |
| Comparable con la norma           | Sí                          | No                |
| Confusor del ciclo diurno         | Eliminado por diseño        | Hay que modelarlo |
| Autocorrelación                   | Moderada                    | Severa            |
| Permite analizar la hora del pico | No                          | Sí                |
| Covariables meteorológicas        | Requieren agregación diaria | Se usan tal cual  |

**Recomendación:** MDA8 como variable objetivo principal, por ser la métrica normativa
y por eliminar el ciclo diurno; el análisis horario, si se quiere, como secundario.

> Si se elige MDA8, quedan tres decisiones **para #14**, no para esta issue: el
> etiquetado de la ventana de 8 h, la regla de completitud (cuántas horas válidas
> exige un promedio y cuántos promedios exige un día), y el resumen diario de cada
> covariable meteorológica.
