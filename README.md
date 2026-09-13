# MA2003B.102.07

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
