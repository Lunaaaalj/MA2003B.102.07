# Presentaciones

Presentaciones breves para audiencias externas al equipo (p. ej. el
socioformador), separadas del reporte de `reports/`. Formato Beamer, no
`elsarticle`, y compilan de forma independiente al reporte.

## Archivos

- `avance_socioformador.tex` — avance del proyecto tras el cambio de
  objetivo (issue #64). No es la presentación final de entrega.

## Cómo compilar

Desde esta carpeta:

```bash
latexmk                    # -> avance_socioformador.pdf
latexmk -c                 # limpia auxiliares
```

## Figuras

No hay una carpeta `figuras/` propia: las diapositivas reutilizan las
figuras ya generadas en `reports/figuras/` vía `\graphicspath`, para no
duplicar archivos entre el reporte y la presentación.

## Estado del contenido

Cada cifra citada debe existir igual en `reports/secciones/`; no se
recalcula ni se redondea distinto. Si un dato todavía no está redactado en
el reporte (por ejemplo, mientras las issues #54/#55 de regresión
logística y discriminante lineal siguen abiertas), la diapositiva
correspondiente se deja marcada como pendiente en vez de rellenarse a
mano.
