# Quarto arranca R con working directory notebooks/ (raíz del proyecto Quarto,
# ver _quarto.yml), y R solo source-ea el .Rprofile del directorio en el que
# arranca. Sin esto, el renv de la raíz del repo nunca se activa y los chunks
# de R quedan con la librería base del sistema, no con renv.lock.
Sys.setenv(RENV_PROJECT = normalizePath(".."))
source("../renv/activate.R")
