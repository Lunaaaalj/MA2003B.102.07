# MA2003B.102.07

Este es un repositorio dedicado a la realización del proyecto del curso de Aplicación de Métodos Multivariados en ciencia de datos por parte del equipo 7 del grupo 102 del Tecnológico de Monterrey.

> Toma en cuenta que este `README.md` deberá ser reescrito para escribir resumen del proyecto y del repositorio, esta guia de collaboration sera agregada a un `CONTRIBUTING.md`.

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

En este caso `Closes #10` "10" seria el numero asignado a la issue.

En este caso `Closes #10` "10" seria el numero asignado a la issue.

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

**8. Merge.** Una vez aprobada y con todas las conversaciones resueltas, la PR se mergea con el botón **Merge pull request**. Nadie mergea a `main` desde su maquina, siempre es por PR.

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

- NO hagas rebase, ni rebase merging. Si tu branch se atrasó respecto a `main`, usa `git merge main` como está explicado arriba. Si algo se enreda, pregunta antes de tocar el historial.
- NO puedes hacer pushes directos a `main`. Siempre antes de hacer commit de tus cambios asegúrate de haber hecho `switch` a otra branch, y de esa branch abres la Pull Request al `main`. Si haces commits en tu `main` local e intentas hacer un push al `origin main`, el remoto te va a detener y vas a estar atorado con commits en tu `main` local.
- Antes de crear una nueva branch para trabajar en algo, asegúrate de crear o asignarte a una issue que explique el objetivo de tu branch.
- Al hacer el/los primeros commits de tu nueva branch, inmediatamente abre una Pull Request en modo draft, y pon en el body de la PR cuál issue se resuelve, usa `Closes #10`, por ejemplo para la issue número 10. El modo draft nos hace saber al equipo que el trabajo está en progreso mientras nos permite ver y discutir los avances.
- Usa commits atómicos, es decir, un commit por cada cambio lógico o bloque de código. No hagas todo de una y luego un solo commit, ni tampoco un commit por cada pedacito de código que escribas: que sea una pieza de trabajo lógica significativa, que aborde exactamente lo que el mensaje del commit indica.
- Haz push a tu branch cada vez que juntes un conjunto significativo de commits, porque Copilot va a revisar la Pull Request y les va a hacer comentarios y recomendaciones. Tomen esos comentarios en cuenta para evitar bugs, errores en los modelos y mejorar la calidad del proyecto en general.
- Mergear una PR a `main` requiere que se resuelvan todas las conversaciones y comentarios, y que se apruebe la Pull Request.
- Si haces un nuevo push después de una aprobación, esta aprobación se eliminará y la PR tendrá que revisarse de nuevo.
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

Cualquier otra cosa, pregunta en el chat del equipo antes de correr comandos que no conozcas.
