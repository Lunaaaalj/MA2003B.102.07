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

## Importante para los miembros del equipo

Para facilitar la colaboración, se aplicarán varias reglas que deberán seguir, esto es muy importante para evitar confusiones, problemas, y conflictos.

### El workflow

Este es el camino que vas a seguir cada vez que trabajes en algo. Si lo sigues tal cual, no te vas a atorar.

**1. Toma una issue.** Antes de escribir una sola línea, crea la issue que explique lo que vas a hacer o asígnate una que ya exista. La issue es el objetivo de tu branch.

**2. Parte de `main` actualizado.** Nunca crees tu branch desde un `main` viejo, porque te vas a topar con conflictos que no eran necesarios.

```bash
git switch main
git pull
git switch -c feat/analisis-pca
```

> En tutoriales y en StackOverflow vas a ver `git checkout main` y `git checkout -b mi-branch`, que hacen lo mismo. Nosotros usamos `switch` porque `checkout` también sirve para descartar cambios de un archivo, y si te equivocas de argumento puedes perder trabajo que no habías commiteado. `switch` solo cambia de branch, y si le pasas algo que no es una branch nada más te marca error.

**3. Trabaja y haz tus commits atómicos.** Cada commit debe ser una pieza de trabajo lógica y completa.

```bash
git add src/analisis_pca.R
git commit -m "feat: agregar calculo de componentes principales"
```

**4. Sube tu branch y abre la PR en draft.** En cuanto tengas tu primer commit (o los primeros), sube la rama y abre la Pull Request en modo draft. No esperes a terminar todo.

```bash
git push -u origin feat/analisis-pca
```

Con GitHub CLI:

```bash
gh pr create --draft --base main --title "feat: analisis de componentes principales" --body "Closes #10"
```

Desde la web: después del `push`, entra al repo en GitHub y te va a aparecer un banner con el botón **Compare & pull request**. Si no aparece, ve a la pestaña **Pull requests** → **New pull request**, elige `main` como base y tu branch como compare. Escribe el título, pon `Closes #10` en el body, y en el botón verde abre el menú y selecciona **Create draft pull request**.

En `Closes #10`, el "10" sería el número asignado a la issue del paso 1. Ponerlo en el body hace que la issue se cierre sola cuando la PR se mergee. El modo draft nos hace saber al equipo que el trabajo está en progreso, mientras nos permite ver y discutir los avances.

**5. Sigue haciendo commits y push.** Cada vez que juntes un conjunto significativo de commits, haz push a tu branch. Si tu PR es de análisis, acuérdate de subir también el PDF renderizado: es lo que hace revisable el trabajo.

**6. Saca la PR de draft.** Cuando el trabajo esté listo, dale a **Ready for review** y pide la revisión del equipo. Ahí es cuando corre la revisión automática de Claude (ver más abajo); los comentarios de Copilot se piden aparte.

**7. Si `main` avanzó mientras trabajabas**, en tu PR te va a aparecer el botón **Update branch**. Dale y GitHub actualiza tu branch con lo nuevo de `main`. Solo si hay conflictos el botón no va a poder, y ahí sí lo resuelves local (con merge, nunca con rebase):

```bash
git switch main
git pull
git switch feat/analisis-pca
git merge main
```

Resuelve los conflictos ahí en tu branch, haz commit y push.

**8. Merge.** Una vez aprobada y con todas las conversaciones resueltas, la PR se mergea con el botón **Merge pull request**. Nadie mergea a `main` desde su máquina, siempre es por PR.

### Convenciones de commits

Usamos Conventional Commits, o sea que el mensaje empieza con un tipo, dos puntos, y una descripción corta en minúsculas y en imperativo (`agregar`, no `agregado` ni `agregue`).

```
feat: agregar matriz de correlacion al EDA
fix: corregir escalamiento antes del PCA
docs: documentar el diccionario de datos
chore: actualizar dependencias de renv
refactor: separar la limpieza de datos en su propia funcion
test: agregar pruebas para la normalizacion
```

- `feat`: funcionalidad, análisis o modelo nuevo.
- `fix`: corrección de un error.
- `docs`: documentación, README, comentarios.
- `chore`: mantenimiento, dependencias, configuración.
- `refactor`: reorganizar código sin cambiar lo que hace.
- `test`: pruebas.

La misma convención aplica para los nombres de branches: `feat/analisis-pca`, `fix/escalamiento-datos`, `docs/diccionario-datos`.

### Las reglas

El workflow de arriba ya cubre el día a día. Esto es lo que no se negocia:

- NO hagas rebase, ni rebase merging. Si tu branch se atrasó respecto a `main`, actualízala con merge como está explicado en el paso 7. Si algo se enreda, pregunta antes de tocar el historial.
- NO puedes hacer pushes directos a `main`. Si haces commits en tu `main` local e intentas hacer un push al `origin main`, el remoto te va a detener y vas a estar atorado con commits en tu `main` local (para salir de eso, ve la sección de abajo).
- Usa commits atómicos. No hagas todo de una y luego un solo commit, ni tampoco un commit por cada pedacito de código que escribas: que sea una pieza de trabajo lógica significativa, que aborde exactamente lo que el mensaje del commit indica.
- Tomen en cuenta los comentarios de Copilot en las PRs, para evitar bugs, errores en los modelos y mejorar la calidad del proyecto en general.
- Mergear una PR a `main` requiere que se resuelvan todas las conversaciones y comentarios, y que se apruebe la Pull Request. Si haces un nuevo push después de una aprobación, esta aprobación se eliminará y la PR tendrá que revisarse de nuevo.
- Puedes hacer force pushes en tus branches personales, pero no es recomendable. Si lo llegas a necesitar, usa `git push --force-with-lease` y nunca sobre una branch en la que esté trabajando alguien más.

### Me atoré, ¿qué hago?

**Hice commits en mi `main` local.** No los pierdas, rescátalos a una branch nueva y regresa tu `main` a como está en el remoto:

```bash
git switch -c feat/mi-trabajo   # tus commits ahora viven aquí
git switch main
git reset --hard origin/main    # tu main queda igual al del remoto
```

**Ya empecé a trabajar pero no he hecho commit y estoy en `main`.** Solo crea la branch, los cambios sin commit se van contigo:

```bash
git switch -c feat/mi-trabajo
```

## Claude en GitHub

El repo tiene integrado el [Claude Code GitHub Action](https://github.com/anthropics/claude-code-action) oficial, así que puedes pedirle ayuda a Claude sin salir de GitHub.

**Menciona `@claude` en un comentario** de un issue o de una PR (o en el cuerpo de un issue nuevo) y va a responder ahí mismo. Sirve para preguntas, para que explique un error, o para pedirle que implemente un cambio, en cuyo caso abre una PR con el trabajo.

```
@claude ¿por qué el catálogo de estaciones no tiene NE3 ni NO3?
@claude revisa de nuevo los chunks que agregué en el último commit
```

Solo funciona para colaboradores con permiso de escritura en el repo, es decir, el equipo.

**Revisión automática.** Cuando marcas tu PR como *Ready for review* (sale del estado draft), Claude la revisa una vez y deja comentarios inline. No corre mientras la PR sigue en draft, ni en cada push, para no gastar la cuota de más. Si quieres otra pasada después de arreglar cosas, pídesela con `@claude`.

Los comentarios de Claude son un apoyo, no una aprobación: la PR sigue necesitando review de una persona del equipo.

## Workflow para los reportes

Este repositorio también será el lugar principal para trabajar en los reportes en LaTeX. Es un poco más complicado que otras plataformas (como Overleaf), donde todos escriben sobre el mismo archivo al mismo tiempo. Aquí cada quien trabaja en su branch, así que hay que tener cuidado para no pisarnos.

El reporte ya está armado en [`reports/`](reports/) y se compila desde esa carpeta con `latexmk` a secas: el `.latexmkrc` ya fija el modo PDF y biber, así que no hacen falta flags. El [`README` de `reports/`](reports/README.md) y la [guía de estilo](reports/guia-estilo.md) tienen el detalle.

**1. Toma una issue.** Cada sección del reporte que haya que trabajar va a estar especificada en una issue. Crea la issue o asígnate a una antes que nada.

**2. Sigue el workflow normal.** Branch nueva desde `main` actualizado, commits atómicos, PR en draft, etc. Todo lo de la sección de arriba aplica igual.

**3. NO hagas más ni menos de lo que dice la issue.** Si escribes de más, es muy probable que te cruces con lo que otra persona está trabajando en su propia issue, y eso se traduce en conflictos de merge sobre el mismo archivo.

**4. Escribe el reporte modularmente.** Esta es la regla más importante para evitar conflictos. **No escribas tu texto directamente en `main.tex`.** Crea un archivo aparte para tu sección y desde `main.tex` solo insértalo:

```latex
% main.tex
\begin{document}
\input{secciones/introduccion}
\input{secciones/metodologia}
\input{secciones/resultados}
\end{document}
```

Así `main.tex` casi nunca cambia (solo cuando se agrega una sección nueva), y cada quien es dueño de su propio archivo. Dos personas trabajando en secciones distintas ya no tocan las mismas líneas.

> `\input{archivo}` le dice al compilador "copia y pega aquí el contenido de ese archivo". Nota que **no lleva la extensión `.tex`**: se escribe `\input{secciones/metodologia}`, no `\input{secciones/metodologia.tex}`.
>
> Vas a ver también `\include{}`, que es parecido pero mete un salto de página forzado antes y después, y no se puede anidar (un archivo incluido no puede incluir a otro). Sirve para capítulos completos, no para secciones. Para nuestro caso, usa `\input`.

**5. Agrega tus referencias en `references.bib`.** En formato BibLaTeX, y solo las tuyas. Ojo: este archivo sí es compartido, así que **agrega tus entradas al final** en lugar de reacomodar las que ya están; si insertas en medio o reordenas, git lo va a ver como conflicto.

Cualquier otra cosa, pregunta en el chat del equipo antes de correr comandos que no conozcas.
