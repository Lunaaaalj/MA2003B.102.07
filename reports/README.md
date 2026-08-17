# Reportes

Aquí vive el reporte del proyecto en LaTeX.

## Estructura

```
reports/
├── main.tex          # preámbulo, portada y los \input de las secciones
├── references.bib    # bibliografía compartida (BibLaTeX)
├── secciones/        # una sección = un archivo = una issue
│   ├── introduccion.tex
│   ├── datos.tex
│   ├── metodologia.tex
│   ├── resultados.tex
│   └── conclusiones.tex
└── figuras/          # imágenes que se insertan con \includegraphics
```

`main.tex` es de todos, así que casi nunca debe cambiar: solo se toca cuando se
agrega una sección nueva. Tu texto va en `secciones/`.

## Cómo compilar

Desde esta carpeta:

```bash
latexmk -pdf main.tex     # genera main.pdf
latexmk -c                # borra los archivos auxiliares
```

Necesitas una distribución de TeX instalada (TeX Live en Linux/Windows,
MacTeX en macOS). `latexmk` se encarga solo de correr LaTeX y biber las veces
que haga falta para que las citas y las referencias cruzadas queden bien.

Si prefieres VS Code, la extensión **LaTeX Workshop** hace lo mismo al guardar.

## Antes de escribir

Lee la sección **"Workflow para los reportes"** del [README de la raíz](../README.md).
En resumen: una issue por sección, una branch por issue, tu texto en tu propio
archivo, y tus referencias al final de `references.bib`.

## Figuras

Las gráficas generadas desde `src/` o `notebooks/` guárdalas aquí en `figuras/`
y insértalas con `\includegraphics{nombre.png}` (el `\graphicspath` de
`main.tex` ya apunta a esta carpeta, no hace falta poner la ruta completa).
Prefiere PDF o SVG convertido a PDF para que no se pixelee al imprimir.
