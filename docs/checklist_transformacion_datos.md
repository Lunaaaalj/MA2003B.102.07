# Checklist — Transformación y escalamiento de datos

Decidir, variable por variable, si transformar o escalar el dataset limpio **es
necesario y conveniente** para el objetivo del equipo — no aplicar todo el
catálogo de técnicas por completitud.

- **Issue:** #35 (repetir #14 con más rigor y participación humana)
- **Depende de:** #13 (dataset limpio)
- **Alimenta:** #15, #17 (declaratoria de uso de IA)
- **Entregable:** `notebooks/02_transformacion_datos.qmd` → `docs/02_transformacion_datos.pdf`
- **Referencia, no resultado a copiar:** `archive/02_transformacion_datos.qmd` (intento
  anterior de #14 — sirve para ver qué se cubrió, no para reproducirlo sin discutirlo)

> **Presupuesto: 4–5 h.** Cada fase trae un tiempo orientativo. Si una fase no
> aplica al objetivo del equipo, se anota "no aplica" y se pasa a la siguiente —
> no se rellena por completitud.

> ⚠️ **Regla del proceso (la razón de ser de #35):** un commit por fase/decisión,
> no todo junto al final. Si en algún punto se usa IA, anotar en el propio
> notebook qué se le pidió y qué se verificó — eso alimenta #17 directamente.

---

## Fase 0 — Preparación (10 min)

- [ ]  Cargar `sima_horario.parquet` ya limpio (post-#13) y confirmar dimensiones
  y variables contra `docs/log_limpieza.md`.
- [ ]  Tener a la mano el objetivo de investigación (#4) y las técnicas que se
  planean para #15 (¿PCA? ¿clustering? ¿regresión?) — de eso depende si
  escalar hace falta o no.

---

## Fase 1 — Diagnóstico: ¿hace falta transformar? (45 min)

- [ ]  Comparar escalas entre variables (rangos, unidades). ¿Hay una variable
  que domine por magnitud si se usa tal cual en un método basado en
  distancias?
- [ ]  Medir asimetría por variable. Marcar cuáles superan un umbral acordado
  en equipo (p. ej. |sesgo| > 0.5) — esas son las candidatas a Fase 2.
- [ ]  Anotar, para cada variable candidata, **por qué** la asimetría importa
  para el método que se piensa usar en #15 (no todos los métodos la
  requieren).
- [ ]  Decisión de fase: lista corta de variables que pasan a Fase 2, con la
  razón de cada una escrita en el notebook.

---

## Fase 2 — Transformación de forma (60–90 min)

Solo para las variables marcadas en Fase 1.

- [ ]  Para cada una, decidir el método (log, log1p, Box-Cox, ninguno) y
  **justificar por qué ese y no otro** — ceros/negativos en los datos
  descartan log puro; interpretabilidad puede pesar más que el ajuste
  estadístico.
- [ ]  Verificar el efecto real: ¿mejora algo que le importe al objetivo
  (linealidad con la variable objetivo, no solo "se ve más normal")?
- [ ]  Documentar explícitamente qué variables **no** se transforman y por qué
  (tan importante como las que sí).

---

## Fase 3 — Discretización (30 min)

- [ ]  Revisar si alguna variable continua se beneficia de convertirse en
  categorías para el objetivo del equipo (p. ej. niveles de calidad del
  aire). Si no aporta, anotar "no aplica" y seguir — no es obligatoria.
- [ ]  Si la variable objetivo ya viene discretizada desde #13, solo
  confirmarlo y enlazar la decisión, no repetirla.

---

## Fase 4 — Atributos derivados (30–45 min)

- [ ]  Revisar qué atributos derivados ya existen desde #13 (`viento_u/v`,
  `hora`, `mes`, `MDA8`, etc. — ver `docs/log_limpieza.md`) para no
  duplicar trabajo.
- [ ]  Decidir si falta alguno nuevo que aporte directamente al objetivo
  (promedio móvil, índice compuesto). Si no, anotarlo y seguir.
- [ ]  Si se agrega algo, verificar si cambia la forma de la variable (puede
  obligar a revisar la Fase 1 para esa columna nueva).

---

## Fase 5 — Escalamiento (45 min)

- [ ]  Confirmar si el método planeado para #15 **requiere** escalar (PCA,
  clustering, distancias sí; árboles o regresión simple con
  variables ya comparables, no necesariamente).
- [ ]  Si aplica, elegir método (estandarización z-score vs. min-max) y
  justificar con el objetivo, no por default.
- [ ]  Verificar el resultado (media/varianza o rango esperado) sobre una
  muestra de columnas.
- [ ]  Anotar advertencias que le sirvan a #15/#17 (p. ej. escalar con
  parámetros del set completo vs. por partición, si aplica).

---

## Fase 6 — Entregable (30–45 min)

- [ ]  Resumen final en el notebook: tabla de decisiones (variable → qué se le
  hizo → por qué), incluyendo las que se dejaron sin tocar.
- [ ]  Confirmar que el historial de commits refleja el proceso por fases, no
  un solo commit final.
- [ ]  Si se usó IA en algún punto, la nota de qué se pidió y qué se verificó
  queda visible en el notebook (no solo en la conversación).
- [ ]  Renderizar y actualizar `docs/02_transformacion_datos.pdf`.
- [ ]  Comentar el resumen en la issue #35 y actualizar el alcance de #15/#17
  con lo decidido aquí.

---

## Fuera de alcance


| Tema                                                                      | Dónde va | Por qué no aquí                                                     |
| ------------------------------------------------------------------------- | --------- | --------------------------------------------------------------------- |
| Elegir el método de análisis multivariado (PCA, clustering, regresión) | #15       | Esta issue solo prepara los datos para lo que #15 decida              |
| Declaratoria formal de uso de IA                                          | #17       | Aquí solo se registra la evidencia; la declaratoria se redacta allá |
| Volver a limpiar/imputar faltantes                                        | #13       | Ya está cerrada; este checklist asume el dataset limpio como entrada |
