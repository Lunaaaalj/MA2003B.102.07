# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es este repositorio

Proyecto del curso **MA2003B (Aplicación de Métodos Multivariados en Ciencia de Datos)**, Tec de Monterrey, grupo 102, equipo 7. Es un repo académico: análisis multivariado sobre datos de calidad del aire del **SIMA** (Sistema Integral de Monitoreo Ambiental, Nuevo León), más el reporte en LaTeX que se entrega.

El idioma del proyecto es **español**: commits, issues, PRs, comentarios de código, nombres de branch y el reporte. Los READMEs de las carpetas scaffolding (`src/`, `tests/`, `notebooks/`, `models/`, `docs/`, `references/`) son plantillas genéricas en inglés que vinieron del template; no son documentación real del proyecto.

El código vive en `src/`: [`importar_datos.py`](src/importar_datos.py) (consolidación, Python) y [`cargar_datos.R`](src/cargar_datos.R) (lectura desde R). En `notebooks/` está [`01_verificacion_calidad.qmd`](notebooks/01_verificacion_calidad.qmd), la auditoría de calidad del consolidado (issue #11).

## Análisis exploratorio: Quarto, no notebooks

**Los análisis se escriben en `.qmd`, no en `.ipynb`.** El equipo migró en agosto 2026 porque los notebooks se llevan mal con git: el JSON con outputs en base64 no se diffea ni se mergea, y el `kernelspec` guardaba el nombre del entorno local de quien lo ejecutara. Un `.qmd` es markdown con chunks, se revisa como cualquier `.py`.

La regla que sale de eso: **la fuente no lleva resultados, el PDF sí.** El `.qmd` solo tiene código y texto; los resultados viven en el PDF renderizado, que **sí se versiona** porque `data/processed/` no está en el repo y sin él nadie puede re-ejecutar nada (~8 min entre regenerar los datos y releer los Excel). Ese PDF es lo que hace revisable una PR de análisis.

```bash
quarto render notebooks/01_verificacion_calidad.qmd   # -> docs/01_verificacion_calidad.pdf
```

- `notebooks/_quarto.yml` define el proyecto: `output-dir: ../docs` y una lista explícita de `render` para que Quarto no toque el `README.md` de la carpeta.
- El motor es `jupyter: python3`. Necesita **`ipykernel`, `nbclient`, `nbformat` y `pyyaml`** en el entorno; sin `pyyaml` el error es `ModuleNotFoundError: No module named 'yaml'`, que parece un bug de Quarto y en realidad es una dependencia de Python faltante.
- Quarto compila el PDF con su propio LuaTeX, independiente del `latexmk` que usa `reports/`. La primera vez se instala solo los paquetes que le faltan.
- Si algún día se escriben chunks de R, Quarto cambia al motor knitr y hace falta el paquete `rmarkdown` en renv — agregándolo con `renv::install()` + `renv::record()`, nunca con `snapshot()`.
- **No configures nbstripout.** Fue una propuesta que se descartó: borra justo los resultados que hacen revisable el trabajo. Con Quarto el problema ya no existe, porque la fuente nunca los tuvo.

## Entornos: son dos, coexisten

El proyecto está preparado para **Python y R a la vez**. Elige según lo que pida la tarea; si no se especifica, mira qué lenguaje ya usan los archivos vecinos.

**Python** — venv en `venv/`, dependencias en `requirements.txt` (pandas, numpy, matplotlib, openpyxl, pyarrow, pytest; **no** hay scipy/sklearn — si un análisis los necesita, instalarlos y actualizar `requirements.txt` con `pip freeze`).

```bash
source venv/bin/activate
pip install -r requirements.txt
```

**R** — gestionado con **renv** (`renv.lock`, R 4.6.1, ~103 paquetes: tidyverse, readxl, ggplot2, googlesheets4). `.Rprofile` activa renv al abrir la sesión, así que basta con:

```r
renv::restore()                      # instalar lo que falte segun renv.lock
renv::record("paquete@1.2.3")        # registrar un paquete nuevo en el lockfile
```

**No corras `renv::snapshot()` en este repo.** `renv/settings.json` tiene `snapshot.type: "implicit"`, así que snapshot recorta el lockfile a los paquetes que aparecen citados en el código y **borra los ~100 restantes** que el equipo instaló para el análisis. Para agregar una dependencia usa `renv::install()` seguido de `renv::record("paquete@version")`, que solo añade la entrada.

## Reporte LaTeX

Vive en `reports/` y se compila **desde esa carpeta**. El `.latexmkrc` ya fija `$pdf_mode = 1` y biber, así que no hacen falta flags:

```bash
cd reports
latexmk        # -> main.pdf
latexmk -c     # limpia auxiliares (incluye bbl, run.xml, spl, synctex.gz)
```

Estructura: clase `elsarticle` a dos columnas (`5p,nonatbib`), babel español, **biblatex + biber** (`style=authoryear`), `cleveref`. `\graphicspath` apunta a `figuras/`, así que las figuras se insertan sin ruta: `\includegraphics{archivo.pdf}`.

Reglas que importan al editar el reporte:

- **Nunca escribir texto directamente en `main.tex`.** Cada sección es un archivo en `secciones/` insertado con `\input{secciones/nombre}` (sin extensión). `main.tex` solo se toca para agregar un `\input` nuevo.
- `natbib` es incompatible con biblatex: por eso la opción `nonatbib`. No usar `\cite` de natbib ni la opción `[times]` de la clase.
- Las opciones de babel-spanish van en `\spanishoptions` **antes** de cargar babel, no como opciones de `\usepackage`.
- `references.bib` es compartido: **agregar entradas al final**, nunca reordenar ni insertar en medio (genera conflictos de merge).
- Los auxiliares y `main.pdf` están en `.gitignore`. Para la entrega final: `git add -f reports/main.pdf`.
- El registro, la densidad, el manejo de números y el criterio de qué detalle de ingeniería de datos vale la pena incluir están en [`reports/guia-estilo.md`](reports/guia-estilo.md). Aplícala al escribir o revisar cualquier `.tex` de `secciones/`, además de las reglas de esta sección.

Nota: hay `main.fdb_latexmk` y `main.out` sueltos en la raíz del repo, restos de una compilación hecha fuera de `reports/`. Son basura; no compiles desde la raíz.

## Datos

La documentación real de los datos (inconsistencias entre años, qué contiene cada archivo, faltantes por parámetro) está en [`data/README.md`](data/README.md). Lo esencial para no tropezar:

- Los seis `BD <año>.xlsx` **no comparten estructura**: 2024 trae las unidades pegadas al encabezado (`CO (ppm)`), 2025 renombró la fecha a `date` y metió una fila de unidades bajo el encabezado, y el número de estaciones va de 13 (2020) a 15 (2024-2025). `src/importar_datos.py` normaliza todo eso; no leas los Excel a mano.
- Cada **hoja es una estación**, no hay columna de estación en el origen.
- `data/processed/` **no se versiona**: se regenera con `python src/importar_datos.py` (~5 min, el padrón es lo lento).
- Las marcas de tiempo son **hora local de pared sin zona horaria**. Al leerlas desde R hay que declarar `tzone <- "UTC"` (no convertir), o se corren 6 horas; `cargar_datos.R` ya lo hace.

`data/raw/` contiene los Excel del SIMA (`BD 2020.xlsx` … `BD 2025.xlsx`, `Etiquetas.xlsx`, inventario y padrón). **Son inmutables**: no se editan ni se sobrescriben. Los datasets limpios van a `data/processed/`, los de terceros a `data/external/` (ninguna de esas carpetas existe todavía; créalas al necesitarlas).

Contexto de dominio en `docs/`: `Rangos de los parámetros del SIMA.pdf` y `Ubicación de las estaciones de monitoreo.docx` — consúltalos antes de interpretar columnas o filtrar valores fuera de rango. Ojo: en esa misma carpeta caen los PDF que genera Quarto, así que ahí conviven material de referencia (inmutable, no se toca) y artefactos regenerables.

Las gráficas que vayan al reporte se guardan en `reports/figuras/`, preferentemente en PDF.

## Pruebas

```bash
source venv/bin/activate
pytest -v
pytest -v -m "not lento"          # salta las que abren Excel
pytest tests/test_importar_datos.py::test_normaliza_encabezados_de_2024
```

La configuración (incluido el marcador `lento`) está en `pytest.ini` en la raíz, así que `pytest` a secas funciona desde cualquier lado.

## Workflow de git (no negociable)

El `README.md` de la raíz es la guía completa del equipo. Lo esencial:

- **Nada de rebase**, ni rebase merging. Si la branch se atrasó respecto a `main`, se actualiza con `git merge main`.
- **Nada de push directo a `main`.** Todo entra por Pull Request aprobada y con conversaciones resueltas.
- Una issue → una branch → una PR. La branch sale de `main` actualizado, con `git switch -c`, y se abre la PR en **draft** desde el primer commit (`Closes #N` en el body).
- **Commits atómicos** y **Conventional Commits en español, imperativo y minúsculas**: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`. Ejemplo: `feat: agregar matriz de correlacion al EDA`. Los nombres de branch siguen la misma convención: `feat/analisis-pca`.
- **No hacer más ni menos de lo que dice la issue** — sobre todo en el reporte, donde escribir de más pisa el trabajo de otra persona.

Al hacer commits en este repo, respeta el estilo del historial (mensajes en español, sin firmas extra a menos que se pidan).

## Claude en GitHub Actions

`.github/workflows/` tiene dos workflows con el action oficial `anthropics/claude-code-action@v1`, autenticados con el secret `CLAUDE_CODE_OAUTH_TOKEN`:

- **`claude.yml`** — modo interactivo. El job solo se levanta si el comentario contiene `@claude`. Ojo: los eventos `issue_comment` siempre usan la versión del workflow que está en `main`, así que editar este archivo en una branch no cambia cómo responde `@claude` hasta que se mergea.
- **`claude-code-review.yml`** — revisión automática, deliberadamente conservadora porque el token está ligado a la suscripción de una persona: corre **solo en `ready_for_review`** (no en `opened` ni en cada push, ya que el equipo abre las PRs en draft desde el primer commit), con `--model claude-sonnet-5`, `--max-turns 20`, `timeout-minutes` y `paths-ignore` para PDFs e imágenes.

Si hay que subir el gasto o bajarlo, los diales son esos: los `types` del trigger, `--max-turns` y el modelo. No agregues `opened`/`synchronize` al trigger de la revisión sin hablarlo con el equipo: multiplica las corridas por cada push a una draft.
