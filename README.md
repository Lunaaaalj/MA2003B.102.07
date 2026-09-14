# MA2003B.102.07

Proyecto del curso **Aplicación de Métodos Multivariados en Ciencia de Datos** (MA2003B), Tecnológico de Monterrey, grupo 102, equipo 7.

Analizamos los datos horarios de calidad del aire del **SIMA** (Sistema Integral de Monitoreo Ambiental de Nuevo León, 2020–2025) para caracterizar el ozono en la Zona Metropolitana de Monterrey y modelar sus excedencias. El pipeline va de los Excel anuales del SIMA a un consolidado limpio, de ahí a un agregado diario por estación, y sobre ese agregado corren las técnicas multivariadas del curso: PCA, análisis factorial, series de tiempo de los factores, regresión logística y análisis discriminante. Todo desemboca en el reporte en LaTeX de [`reports/`](reports/).

## Estructura del repositorio

```
data/          raw/ (Excel del SIMA, inmutables) y processed/ (generado, casi todo ignorado por git)
src/           pipeline en Python (importar_datos, limpieza, agregacion_diaria, factorial) y cargar_datos.R
notebooks/     analisis en Quarto (.qmd) - la fuente, sin resultados
docs/          PDFs renderizados de los .qmd + documentacion de datos y de referencia
reports/       reporte en LaTeX (main.tex, secciones/, figuras/, references.bib)
presentations/ avances presentados al socioformador
tests/         pruebas de pytest del codigo de src/
archive/       analisis que se descartaron y se conservan como historia
```

La documentación de los datos (inconsistencias entre años, faltantes por parámetro, diccionario) está en [`data/README.md`](data/README.md) y en [`docs/`](docs/).

## Entornos

El proyecto usa **Python y R a la vez**; elige según lo que pida la tarea.

**Python** — entorno virtual y `requirements.txt` (pandas, numpy, scipy, scikit-learn, statsmodels, factor_analyzer, matplotlib, openpyxl, pyarrow, pytest):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Si un análisis necesita una librería nueva, instálala y actualiza `requirements.txt` con `pip freeze`: ese archivo es el contrato del equipo.

**R** — gestionado con **renv** (`renv.lock`, R 4.6.1; tidyverse, readxl, ggplot2, googlesheets4). El `.Rprofile` activa renv al abrir la sesión:

```r
renv::restore()                 # instalar lo que falte segun renv.lock
renv::install("paquete")        # agregar una dependencia nueva...
renv::record("paquete@1.2.3")   # ...y registrarla en el lockfile
```

> **No corras `renv::snapshot()`.** El lockfile está en modo `implicit`, así que snapshot lo recorta a los paquetes citados en el código y borra los ~100 restantes. Para agregar dependencias, `install()` + `record()`.

### Desarrollo en Codespaces (sin instalación local)

`.devcontainer/` deja el repo listo para abrirse en GitHub Codespaces con LaTeX (`latexmk`, `biber`, `elsarticle`), Python y R. Al crear el Codespace, el `postCreateCommand` crea el entorno `.venv`, instala `requirements.txt` y corre `renv::restore(prompt = FALSE)` (nunca `snapshot()`).

## Pipeline de datos

`data/processed/` no se versiona (salvo los datasets finales que sí están commiteados), así que se regenera:

```bash
source venv/bin/activate
python src/importar_datos.py      # consolida los BD <anio>.xlsx (~5 min) -> sima_horario.parquet
python src/limpieza.py            # -> sima_limpio_horario.csv / sima_limpio_diario.csv
python src/agregacion_diaria.py   # una fila por dia-estacion -> sima_diario_modelado.parquet
```

Los seis `BD <año>.xlsx` no comparten estructura entre sí y cada hoja es una estación; `src/importar_datos.py` normaliza todo eso, no los leas a mano. Desde R, `source("src/cargar_datos.R")` carga el mismo dataframe con las marcas de tiempo ya declaradas como hora local de pared.

## Análisis: Quarto, no notebooks

Los análisis se escriben en **`.qmd`**, no en `.ipynb`: un notebook es JSON con outputs en base64 que no se diffea ni se mergea, y un `.qmd` se revisa como cualquier archivo de código.

De ahí sale la regla: **la fuente no lleva resultados, el PDF sí.** El `.qmd` solo tiene código y texto; los resultados viven en el PDF renderizado, que se versiona en `docs/` porque sin él nadie puede revisar la PR sin re-ejecutar el pipeline completo.

```bash
quarto render notebooks/07_pca.qmd     # -> docs/07_pca.pdf
quarto render notebooks                # renderiza todos los .qmd del proyecto
```

El motor es `jupyter: python3` y necesita `ipykernel`, `nbclient`, `nbformat` y `pyyaml` en el entorno (ya están en `requirements.txt`); si falta `pyyaml`, el error es un `ModuleNotFoundError: No module named 'yaml'` que parece un bug de Quarto y no lo es.

## Pruebas

```bash
source venv/bin/activate
pytest -v
pytest -v -m "not lento"     # salta las que abren los Excel de data/raw/
```

La configuración vive en `pytest.ini` en la raíz, así que `pytest` a secas funciona desde cualquier carpeta.

## Reporte

El reporte en LaTeX vive en [`reports/`](reports/) y se compila desde esa carpeta con `latexmk` a
secas: el `.latexmkrc` ya fija el modo PDF y biber, así que no hacen falta flags. Cada sección es
un archivo en `reports/secciones/` que `main.tex` inserta con `\input`; las figuras van en
`reports/figuras/`, preferentemente en PDF. El detalle está en el [`README` de
`reports/`](reports/README.md) y en la [guía de estilo](reports/guia-estilo.md).

## Cómo colaborar

Todo el flujo de trabajo del equipo —issues, branches, commits, Pull Requests, el uso de Claude en
GitHub y las reglas para escribir el reporte sin pisarse— está en
[`CONTRIBUTING.md`](CONTRIBUTING.md). Léelo antes de tu primer commit.
