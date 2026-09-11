# MA2003B.102.07

> ## ⚠️ Pendiente: actualizar el reporte al 2025 completo
>
> El 11 de septiembre de 2026 se recibió la versión completa de `BD 2025.xlsx`
> (antes cortaba el 30 de junio). La rama `anio_2025` regeneró **todo** el
> pipeline, las notebooks y sus PDF en `docs/`, y los parquets versionados.
> Los `.tex` de `reports/secciones/` **no se tocaron**: cada uno tiene dueño y
> se corrige en su propia issue. Lo que hay que cambiar, con la cifra vieja →
> nueva y la notebook de donde sale:
>
> **Cambios de fondo (no solo de número):**
>
> - **Ya no existe el "desbalance estacional" de la validación.** 2025 completo
>   reparte 24.6 / 25.4 / 24.0 / 26.0 % por temporada, igual que el
>   entrenamiento. Lo que sí persiste es que 2025 es el año de ozono más alto
>   de la serie (tasa base 42.2 % día-estación contra 29.3 %); es un efecto de
>   año, no de calendario (`docs/05_estacionalidad_ozono.pdf` §5). Todo párrafo
>   que diga "le sobra primavera y le falta otoño" se reescribe.
> - **Los AUC de validación bajan.** Logística 0.893 → 0.850, discriminante
>   0.893 → 0.846 (`docs/analisis_discriminante.pdf`); nowcasting 0.927 → 0.898
>   (`docs/autorregresivo_logistico.pdf`). El AUC esperado en un año cualquiera
>   sigue siendo 0.80 (panel) y 0.878 (área), y ahora 2025 cae dentro de ese
>   rango en vez de en su extremo.
> - **Los tres factores son estables fuera del ajuste**: congruencia de Tucker
>   0.973 / 0.939 / 0.924 en 2025 (antes la ventilación daba 0.826 y se
>   atribuía a la ventana estacional; `docs/09_extraccion_factorial.pdf` §7.2).
> - **El pronóstico a un día queda firme**: 0.779 contra 0.667 de climatología,
>   p < 10⁻⁴ (antes 0.814 vs 0.760 con p = 0.09; `docs/pronostico_excedencia.pdf`).
>
> **Por archivo:**
>
> - `seleccion_datos.tex` (l. 70): quitar "con la salvedad de que 2025 cubre
>   únicamente hasta el 30 de junio". Cobertura 2021-01-01 → 2025-12-31.
> - `diccionario_datos.tex`: tabla de faltantes por estación y año (l. 293+),
>   columna 2025; "NO3 con 30.3 % en 2025" (l. 114). Cifras en
>   `docs/01_verificacion_calidad.pdf` §2. Los conteos por estación (CE 52,605…)
>   no cambian.
> - `diccionario_transformadas.tex` (l. 6): 574,343 → 640,583 filas horarias.
> - `diccionario_datos_transformadas.tex` (l. 8–9): 23,931 → 26,691 día-estación;
>   "30 de junio" → "31 de diciembre de 2025". Tabla de parámetros Box-Cox
>   (l. 159+): regenerar desde `data/processed/transformacion_diaria_parametros.csv`
>   — `SR_acum` ahora sí se transforma (sesgo 0.53, λ = 0.755); son 13
>   candidatas, no 12.
> - `transformaciones.tex` (tabla de sesgo l. 61): recalcular desde
>   `docs/transformaciones.pdf`; `RAINF` pasa de 238 a 145 de sesgo y `SR`
>   queda en 1.02 tras Box-Cox.
> - `descript_quant.tex`: toda la tabla de estadísticos horarios (l. 66 y
>   vecinas) y el n listwise (l. 157: 14,719 de 23,931 → recalcular; con las 16
>   continuas es 15,856 de 26,691, 59.4 %). Correlaciones diarias:
>   `WSR_media`–`WSR_min` 0.72 → 0.71, `PM10`–`PM2.5` 0.69 → 0.70; KMO 0.661 →
>   0.660 y `TOUT_max` (0.596) se suma a las variables bajo 0.6
>   (`docs/06_correlacion_diaria.pdf` §4–5).
> - `eda_cualitativas.tex`: n = 574,343 → 640,583 (l. 10, 23); l. 62 quitar
>   "la serie termina el 30 de junio de 2025"; l. 120 cobertura → 2025-12-31;
>   tabla de excedencias (l. 93, 103): 65 ppb 2,400 (10.65 %) → 2,825
>   (11.25 %), 60 ppb → 4,236 (16.88 %), 51 ppb 6,917 (30.70 %) → 8,021
>   (31.96 %) sobre 25,100 válidos; l. 205, 209 los mismos porcentajes.
>   `NO3` cobertura 22,631 h → ver `docs/04_eda_cualitativas.pdf` §2.
> - `objetivo_tecnicas.tex` (l. 21, 25): 10.65 % → 11.25 %; 30.70 % → 31.96 %.
> - `pca.tex`: eigenvalores y cargas (`docs/07_pca.pdf` §3–4): 3 componentes,
>   55.9 % (igual); distancia al codo PC4 1.843/PC3 1.786 → 1.839/1.783;
>   curvatura 1.133/0.259 → 1.121/0.267; `SR_acum` +0.65 → +0.64,
>   `PRS_media` +0.39 → +0.40. El párrafo de "2025 termina el 30 de junio"
>   sobre las medias de validación se sustituye por el efecto de año.
> - `regresion_logistica.tex` — es la sección con más cambios:
>   - tasa base de validación 41.50 % → 43.97 % (l. 85);
>   - AUC 0.893 → 0.850, umbral de Youden 0.288 → 0.282, sensibilidad 0.831 →
>     0.698, especificidad 0.824 → 0.853 (l. 87); con umbral 0.5: sensibilidad
>     0.518 → 0.326, especificidad 0.942 → 0.964 (l. 89);
>   - discriminante: AUC 0.846, umbral 0.249, sensibilidad 0.758, especificidad
>     0.788; coeficientes LD1 (l. 123+) desde `docs/analisis_discriminante.pdf`;
>   - l. 147 "indistinguibles… DeLong p = 0.80" → AUC 0.850 vs 0.846, DeLong
>     p = 0.0002, diferencia estadísticamente real y sin consecuencia práctica;
>     concordancia 93.8 %; l. 165 ahora el discriminante detecta más
>     excedencias (0.758 vs 0.698) a cambio de menos especificidad;
>   - l. 171 autocorrelación: 17,029 filas / 1,641 días → 18,631 / 1,826;
>   - l. 177 **eliminar "Desbalance estacional de la partición"** y sustituir
>     por "Validación en un año atípico" (44 % vs 29 % de tasa base);
>   - tabla de momios (l. 54–56): siguen siendo los del PCA por unidad
>     (1.47/1.58/1.22). Por desviación estándar valen 2.173/2.188/1.278; si se
>     migra a factores, 1.92/0.90/2.78 (`docs/analisis_discriminante.pdf`,
>     "Contraste con las componentes principales"). Los IC corregidos por
>     conglomerado de día: ventilación [0.84, 0.97], forzamiento [2.48, 3.10].
> - Sección de nowcasting (si ya existe en `secciones/`): AUC 0.927 → 0.898,
>   IC [0.867, 0.929]; sensibilidad 88.7 → 75.9 %, especificidad 81.2 → 84.1 %;
>   skill de Brier 0.572 → 0.436; climatología 0.762 → 0.668, persistencia
>   0.737 → 0.717; generalización 0.878 [0.859, 0.897], rango 0.840–0.915;
>   subpredicción: media predicha 0.338 vs 0.466 observada; OR foto 3.66 →
>   3.69, comb 2.35 → 2.37, y₍t−1₎ 3.84 → 3.83. Pronóstico: a un día 0.779 vs
>   0.667 (p < 10⁻⁴), a dos 0.704 vs 0.665 (p = 0.03), oráculo a 7 días 0.868.
> - Figuras: todas las de `reports/figuras/` ya están regeneradas; basta
>   recompilar `reports/`.
>
> Cuando una sección quede corregida, borra su viñeta de esta lista.

Este es un repositorio dedicado a la realización del proyecto del curso de Aplicación de Métodos Multivariados en ciencia de datos por parte del equipo 7 del grupo 102 del Tecnológico de Monterrey.

> Toma en cuenta que este `README.md` deberá ser reescrito para escribir resumen del proyecto y del repositorio, esta guía de colaboración será movida a un `CONTRIBUTING.md`.

## Importante para los miembros del equipo

Para facilitar la colaboración, se aplicarán varias reglas que deberán seguir, esto es muy importante para evitar confusiones, problemas, y conflictos.

### Desarrollo en Codespaces (sin instalación local)

Este repositorio incluye una configuración de Dev Container en `.devcontainer/` para abrirlo en GitHub Codespaces con todo listo:

- LaTeX (`latexmk`, `biber`, clase `elsarticle` y paquetes necesarios para compilar `reports/main.tex`).
- Python con entorno virtual `.venv` e instalación de `requirements.txt`.
- R `4.6.1` con `renv::restore(prompt = FALSE)` al crear el contenedor.

Al crear el Codespace, el `postCreateCommand` instala automáticamente dependencias de Python y restaura paquetes de R desde `renv.lock` (sin ejecutar `renv::snapshot()`).

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

**5. Sigue haciendo commits y push.** Cada vez que juntes un conjunto significativo de commits, haz push a tu branch. Copilot va a ir revisando la PR y dejando comentarios.

**6. Saca la PR de draft.** Cuando el trabajo esté listo, dale a **Ready for review** y pide la revisión del equipo.

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

El reporte ya está armado en [`reports/`](reports/), y se compila con `latexmk -pdf main.tex` desde esa carpeta.

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
