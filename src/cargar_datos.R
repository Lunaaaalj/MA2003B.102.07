# cargar_datos.R -- acceso desde R a los datos ya consolidados (issue #9).
#
# La consolidación de los Excel crudos la hace src/importar_datos.py (Python).
# Este archivo NO vuelve a leer data/raw/: solo lee los Parquet/CSV que aquel
# script deja en data/processed/, para que las dos mitades del equipo trabajen
# exactamente sobre los mismos datos.
#
# Si data/processed/ está vacío, primero hay que correr, desde la raíz del repo:
#     source venv/bin/activate
#     python src/importar_datos.py
#
# Uso:
#     source("src/cargar_datos.R")
#     sima <- cargar_sima()          # 2020-2025, una fila por (fecha, estación)
#     sima <- cargar_sima(anios = 2024:2025)
#     est  <- cargar_etiquetas("estaciones")

# Solo se depende de nanoparquet (lector de Parquet ligero, ya en renv.lock).
# A propósito NO se usa dplyr/tibble aquí: así este archivo funciona aunque
# todavía no se haya corrido renv::restore() completo. Los data.frame que
# devuelve se pueden pasar a dplyr sin problema.
library(nanoparquet)

# Ruta del repo deducida de la ubicación de este archivo cuando se usa
# source(); si no se puede, se cae al directorio de trabajo actual.
.raiz_proyecto <- function() {
  ruta <- tryCatch(normalizePath(sys.frame(1)$ofile), error = function(e) NA_character_)
  if (!is.na(ruta)) return(dirname(dirname(ruta)))
  getwd()
}

RUTA_PROCESSED <- file.path(.raiz_proyecto(), "data", "processed")

.exigir <- function(archivo) {
  ruta <- file.path(RUTA_PROCESSED, archivo)
  if (!file.exists(ruta)) {
    stop(sprintf(
      "No existe %s.\nCorre primero:  python src/importar_datos.py", ruta
    ), call. = FALSE)
  }
  ruta
}

#' Datos horarios del SIMA, 2020-2025, ya consolidados.
#'
#' @param anios vector de años a conservar; NULL (default) devuelve todos.
#' @return tibble con fecha, estacion, anio y los 15 parámetros medidos.
cargar_sima <- function(anios = NULL) {
  datos <- as.data.frame(read_parquet(.exigir("sima_horario.parquet")))
  datos$estacion <- as.factor(datos$estacion)
  # Las horas del SIMA son hora local de pared y en Parquet van sin zona
  # horaria. POSIXct siempre tiene zona, así que R las asume UTC y las
  # imprime en la del sistema: 2025-01-01 00:00 se vería como 2024-12-31
  # 18:00. Se DECLARA la zona (no se convierte) para dejar la hora intacta;
  # usar as.POSIXct(tz=) aquí correría los datos 6 horas de verdad y
  # arruinaría cualquier análisis de ciclo diario.
  attr(datos$fecha, "tzone") <- "UTC"
  if (!is.null(anios)) datos <- datos[datos$anio %in% anios, , drop = FALSE]
  datos
}

#' Catálogos de Etiquetas.xlsx.
#'
#' @param cual "estaciones", "contaminantes", "meteorologicos" o "banderas".
cargar_etiquetas <- function(cual = c("estaciones", "contaminantes",
                                      "meteorologicos", "banderas")) {
  cual <- match.arg(cual)
  read.csv(.exigir(sprintf("etiquetas_%s.csv", cual)),
           fileEncoding = "UTF-8", check.names = FALSE)
}

#' Inventario de emisiones SABANA 2018.
#'
#' @param ambito "zmm" (zona metropolitana de Monterrey) o "nl" (todo el estado).
cargar_inventario <- function(ambito = c("zmm", "nl")) {
  ambito <- match.arg(ambito)
  as.data.frame(read_parquet(.exigir(sprintf("inventario_%s_2018.parquet", ambito))))
}

#' Padrón vehicular de la Secretaría de Medio Ambiente (~1 millón de filas).
cargar_padron <- function() {
  as.data.frame(read_parquet(.exigir("padron_vehicular.parquet")))
}

#' Tabla parámetro -> unidad de medición, para etiquetar ejes y tablas.
cargar_unidades <- function() {
  read.csv(.exigir("unidades.csv"), fileEncoding = "UTF-8")
}
