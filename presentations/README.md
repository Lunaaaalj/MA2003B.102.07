# Presentaciones

Presentaciones breves para audiencias externas al equipo (p. ej. el
socioformador), separadas del reporte de `reports/`. Formato Beamer, no
`elsarticle`, y compilan de forma independiente al reporte.

## Archivos

Dos versiones del mismo avance (issue #64), con las mismas cifras y la
misma estructura de 3 diapositivas de contenido, pero redactadas para
audiencias distintas:

1. **Objetivo y tratamiento de los datos** — el objetivo del análisis y
   qué se hizo con los datos (imputación, atípicos conservados, errores
   de medición eliminados). El ACP se resume en un párrafo: no es el
   tema de la presentación.
2. **Los dos modelos** — regresión logística y discriminante lineal en
   una sola diapositiva, con su comparación.
3. **Conclusiones** — las cuatro de la subsección homónima de
   `reports/secciones/regresion_logistica.tex`.

Las versiones son:

- `avance_socioformador.tex` — versión **simple**: lenguaje llano, sin
  jerga estadística.
- `avance_socioformador_tecnico.tex` — versión **técnica**: misma
  estructura y cifras, con terminología estadística (razones de momios,
  homocedasticidad, prueba de DeLong, etc.) para una audiencia con ese
  conocimiento previo.

Ninguna es la presentación final de entrega.

## Cómo compilar

Desde esta carpeta:

```bash
latexmk avance_socioformador.tex           # -> avance_socioformador.pdf
latexmk avance_socioformador_tecnico.tex   # -> avance_socioformador_tecnico.pdf
latexmk -c                                 # limpia auxiliares de ambas
```

## Figuras

No hay una carpeta `figuras/` propia: las diapositivas reutilizan las
figuras ya generadas en `reports/figuras/` vía `\graphicspath`, para no
duplicar archivos entre el reporte y la presentación.

## Estado del contenido

Cada cifra citada debe existir igual en `reports/secciones/`; no se
recalcula ni se redondea distinto. Si un dato todavía no está redactado
en el reporte, la diapositiva correspondiente se deja marcada como
pendiente en vez de rellenarse a mano.
