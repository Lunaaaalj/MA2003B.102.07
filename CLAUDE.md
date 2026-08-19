# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es este repositorio

Proyecto del curso **MA2003B (Aplicación de Métodos Multivariados en Ciencia de Datos)**, Tec de Monterrey, grupo 102, equipo 7. Es un repo académico: análisis multivariado sobre datos de calidad del aire del **SIMA** (Sistema Integral de Monitoreo Ambiental, Nuevo León), más el reporte en LaTeX que se entrega.

El idioma del proyecto es **español**: commits, issues, PRs, comentarios de código, nombres de branch y el reporte. Los READMEs de las carpetas scaffolding (`src/`, `tests/`, `notebooks/`, `models/`, `docs/`, `references/`) son plantillas genéricas en inglés que vinieron del template; no son documentación real del proyecto.

El código vive en `src/`: [`importar_datos.py`](src/importar_datos.py) (consolidación, Python) y [`cargar_datos.R`](src/cargar_datos.R) (lectura desde R). `notebooks/` sigue vacío.

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

Nota: hay `main.fdb_latexmk` y `main.out` sueltos en la raíz del repo, restos de una compilación hecha fuera de `reports/`. Son basura; no compiles desde la raíz.

## Datos

La documentación real de los datos (inconsistencias entre años, qué contiene cada archivo, faltantes por parámetro) está en [`data/README.md`](data/README.md). Lo esencial para no tropezar:

- Los seis `BD <año>.xlsx` **no comparten estructura**: 2024 trae las unidades pegadas al encabezado (`CO (ppm)`), 2025 renombró la fecha a `date` y metió una fila de unidades bajo el encabezado, y el número de estaciones va de 13 (2020) a 15 (2024-2025). `src/importar_datos.py` normaliza todo eso; no leas los Excel a mano.
- Cada **hoja es una estación**, no hay columna de estación en el origen.
- `data/processed/` **no se versiona**: se regenera con `python src/importar_datos.py` (~5 min, el padrón es lo lento).
- Las marcas de tiempo son **hora local de pared sin zona horaria**. Al leerlas desde R hay que declarar `tzone <- "UTC"` (no convertir), o se corren 6 horas; `cargar_datos.R` ya lo hace.

`data/raw/` contiene los Excel del SIMA (`BD 2020.xlsx` … `BD 2025.xlsx`, `Etiquetas.xlsx`, inventario y padrón). **Son inmutables**: no se editan ni se sobrescriben. Los datasets limpios van a `data/processed/`, los de terceros a `data/external/` (ninguna de esas carpetas existe todavía; créalas al necesitarlas).

Contexto de dominio en `docs/`: `Rangos de los parámetros del SIMA.pdf` y `Ubicación de las estaciones de monitoreo.docx` — consúltalos antes de interpretar columnas o filtrar valores fuera de rango.

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
