# src/

Código reutilizable del proyecto. Lo exploratorio va en [`notebooks/`](../notebooks/)
y debe llamar a las funciones de aquí, no reimplementarlas.

## Archivos

| Archivo | Qué hace |
|---|---|
| [`importar_datos.py`](importar_datos.py) | Lee los Excel de `data/raw/`, resuelve las inconsistencias entre años y escribe `data/processed/`. Es el punto de partida de la Parte II (issue #9). |
| [`cargar_datos.R`](cargar_datos.R) | Acceso desde R a lo que ya generó el script anterior. No vuelve a leer `data/raw/`. |

## Python

```bash
source venv/bin/activate
pip install -r requirements.txt

python src/importar_datos.py              # construye todo data/processed/
python src/importar_datos.py --solo bd    # bd | etiquetas | inventario | padron
python src/importar_datos.py --forzar     # regenera aunque ya exista
```

Desde un notebook o desde otro script:

```python
from src.importar_datos import cargar_bd, cargar_etiquetas, cargar_inventario

sima = cargar_bd()                    # 2020-2025 consolidado
sima = cargar_bd(anios=[2024, 2025])  # solo unos años
```

## R

Requiere `nanoparquet` (ya está en `renv.lock`):

```r
renv::restore()

source("src/cargar_datos.R")
sima <- cargar_sima()                 # data.frame, mismas 18 columnas
est  <- cargar_etiquetas("estaciones")
inv  <- cargar_inventario("zmm")
```

`cargar_datos.R` a propósito solo depende de `nanoparquet` y no de dplyr, para que
funcione aunque `renv::restore()` todavía no haya terminado. Los `data.frame` que
devuelve se pasan a dplyr sin problema.

## Pruebas

```bash
pytest -v
pytest -v -m "not lento"   # salta las que abren los Excel
```

## Por qué los datos se consolidan una sola vez, en Python

Leer los nueve Excel tarda varios minutos (el padrón vehicular solo son 60 MB y un
millón de filas). Hacerlo en cada sesión, y por duplicado en los dos lenguajes, era
tiempo perdido y una invitación a que Python y R terminaran analizando datos
ligeramente distintos. La conversión corre una vez y deja Parquet, que conserva los
tipos y lo leen los dos lenguajes.
