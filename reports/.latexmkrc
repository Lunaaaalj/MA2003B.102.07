# Configuracion de latexmk para este reporte.
# latexmk lee este archivo solo, no hay que pasarle nada.
#
# Con esto basta con correr, DESDE ESTA CARPETA:
#     latexmk
#
# Ojo: latexmk por defecto genera DVI (un formato viejo, previo al PDF).
# La linea de abajo lo cambia a PDF para que no tengas que acordarte de -pdf.

$pdf_mode = 1;        # 1 = pdflatex -> main.pdf   (0 seria DVI)
$bibtex_use = 2;      # corre biber automaticamente y limpia el .bbl
$out_dir = '.';       # el PDF sale aqui mismo, junto a main.tex

# Que borra 'latexmk -c' ademas de los auxiliares que ya conoce
$clean_ext = 'bbl run.xml spl synctex.gz';
