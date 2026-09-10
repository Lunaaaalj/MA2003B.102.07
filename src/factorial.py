"""Maquinaria del analisis factorial exploratorio (issue de #54-bis).

Vive aqui y no dentro del .qmd porque son algoritmos, no argumento: la notebook
se queda con los criterios y la interpretacion, que es lo que se revisa.

Se implementan a mano por una razon concreta: `factor_analyzer==0.5.1` -la
version mas reciente publicada y la que fija requirements.txt- llama a
`sklearn.utils.check_array(force_all_finite=...)`, argumento que scikit-learn
removio en la serie 1.9 que este proyecto usa. La libreria no corre y no hay
version posterior a la cual subir.

La solucion se valido contra `psych::fa(fm="pa", rotate="varimax")` de R sobre
el mismo bloque de 13 predictores: las cargas coinciden hasta orden y signo de
los factores (maxima diferencia 0.03) y las comunalidades a la milesima.

Correr las pruebas:

    source venv/bin/activate
    pytest tests/test_factorial.py -v
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "ejes_principales",
    "varimax",
    "oblimin",
    "puntajes_bartlett",
    "residuos",
    "determinacion",
    "congruencia",
]


def ejes_principales(R: np.ndarray, k: int, iters: int = 1000,
                     tol: float = 1e-8) -> tuple[np.ndarray, np.ndarray]:
    """Ejes principales iterados (PAF) sobre la matriz de correlacion `R`.

    Arranca poniendo la correlacion multiple al cuadrado (SMC) en la diagonal
    -la estimacion inicial estandar de la comunalidad- y repite: descompone la
    matriz reducida, recalcula comunalidades desde las cargas, vuelve a
    ponerlas en la diagonal. Para cuando el cambio maximo baja de `tol`.

    A diferencia de maxima verosimilitud no supone normalidad multivariada, lo
    que importa aqui porque las variables pasaron por Box-Cox pero no quedaron
    normales.

    Devuelve `(cargas_sin_rotar, comunalidades)`. Una comunalidad > 1 es un
    caso Heywood: el modelo no admite esa variable y hay que podarla.
    """
    h2 = 1 - 1 / np.diag(np.linalg.inv(R))
    Rh = R.copy()
    for _ in range(iters):
        np.fill_diagonal(Rh, h2)
        lam, V = np.linalg.eigh(Rh)
        orden = lam.argsort()[::-1]
        lam, V = lam[orden][:k], V[:, orden][:, :k]
        L = V * np.sqrt(np.clip(lam, 0, None))
        nueva = (L ** 2).sum(1)
        if np.abs(nueva - h2).max() < tol:
            return L, nueva
        h2 = nueva
    return L, h2


def varimax(A: np.ndarray, iters: int = 500,
            tol: float = 1e-9) -> np.ndarray:
    """Rotacion ortogonal varimax por el algoritmo SVD de Kaiser.

    Maximiza la varianza de las cargas al cuadrado dentro de cada factor, que
    es la forma operativa de pedir estructura simple: cada variable cargando
    fuerte en un factor y cerca de cero en los demas.

    Al ser ortogonal preserva `A @ A.T`, de modo que reproduce exactamente las
    mismas comunalidades y el mismo ajuste que la solucion sin rotar.
    """
    p, k = A.shape
    Rot = np.eye(k)
    for _ in range(iters):
        Lr = A @ Rot
        u, _, vt = np.linalg.svd(
            A.T @ (Lr ** 3 - Lr @ np.diag((Lr ** 2).sum(0)) / p))
        nueva = u @ vt
        if np.abs(nueva - Rot).max() < tol:
            return A @ nueva
        Rot = nueva
    return A @ Rot


def _criterio_oblimin(L: np.ndarray, gamma: float) -> tuple[float, np.ndarray]:
    """Criterio oblimin y su gradiente. gamma=0 es quartimin."""
    p, k = L.shape
    N = np.ones((k, k)) - np.eye(k)
    C = np.eye(p) - gamma * np.ones((p, p)) / p
    X = C @ (L ** 2) @ N
    return (L ** 2 * X).sum() / 4, L * X


def oblimin(A: np.ndarray, gamma: float = 0.0, iters: int = 1000,
            tol: float = 1e-6) -> tuple[np.ndarray, np.ndarray]:
    """Rotacion oblicua por proyeccion de gradiente (Bernaards y Jennrich 2005).

    Deja que los factores correlacionen. Devuelve `(patron, phi)`: la matriz de
    patron -coeficientes de regresion de cada variable sobre los factores- y la
    matriz de correlacion entre factores.

    Ojo al interpretar: con rotacion oblicua el patron ya no son correlaciones
    variable-factor. Esas son la matriz de estructura, `patron @ phi`.
    """
    T = np.eye(A.shape[1])
    paso = 1.0
    Ti = np.linalg.inv(T)
    L = A @ Ti.T
    f, Gq = _criterio_oblimin(L, gamma)
    G = -((L.T @ Gq @ Ti).T)
    for _ in range(iters):
        Gp = G - T * (T * G).sum(0)          # proyecta al espacio tangente
        s = np.sqrt((Gp ** 2).sum())
        if s < tol:
            break
        paso *= 2
        for _ in range(50):                  # busqueda de linea con retroceso
            M = T - paso * Gp
            Tt = M / np.sqrt((M ** 2).sum(0))
            Ti = np.linalg.inv(Tt)
            Lt = A @ Ti.T
            ft, Gqt = _criterio_oblimin(Lt, gamma)
            if ft < f - 0.5 * s ** 2 * paso:
                break
            paso /= 2
        T, L, f, Gq = Tt, Lt, ft, Gqt
        G = -((L.T @ Gq @ Ti).T)
    return L, T.T @ T


def puntajes_bartlett(Z: np.ndarray, L: np.ndarray,
                      h2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Puntajes factoriales de Bartlett y la matriz de pesos que los produce.

    `f = (L' U^-1 L)^-1 L' U^-1 z`, con `U` la diagonal de unicidades. Son los
    estimadores de minimos cuadrados ponderados y son insesgados, a diferencia
    de los puntajes de regresion, que encogen hacia cero.

    Se devuelve tambien `W` para poder aplicar a validacion los pesos del
    ajuste de entrenamiento, sin reestimar nada sobre 2025.
    """
    Ui = np.diag(1 / (1 - h2))
    W = np.linalg.inv(L.T @ Ui @ L) @ L.T @ Ui
    return Z @ W.T, W


def residuos(R: np.ndarray, L: np.ndarray,
             h2: np.ndarray) -> tuple[np.ndarray, float]:
    """Residuos `R - (LL' + U)` y su raiz cuadratica media fuera de la diagonal.

    El RMSR es la medida de ajuste que no depende de `n`, a diferencia de la
    chi-cuadrada de maxima verosimilitud, que con 16 mil observaciones rechaza
    cualquier modelo. La convencion lo quiere por debajo de 0.08.
    """
    res = R - (L @ L.T + np.diag(1 - h2))
    fuera = res[~np.eye(len(R), dtype=bool)]
    return res, float(np.sqrt((fuera ** 2).mean()))


def determinacion(R: np.ndarray, L: np.ndarray) -> np.ndarray:
    """Coeficientes de determinacion de los puntajes factoriales.

    Es la correlacion entre el puntaje estimado y el factor que pretende medir,
    `rho = sqrt(diag(L' R^-1 L))`. Existe porque los puntajes factoriales se
    estiman y no se calculan: a diferencia de una componente principal, que es
    una combinacion lineal exacta de las variables, el factor es latente y
    ningun puntaje lo recupera sin error.

    Convencion: por encima de 0.90 se considera deseable y por encima de 0.80
    utilizable. Por debajo, la indeterminacion factorial es lo bastante grande
    como para que dos conjuntos de puntajes igualmente validos puedan
    correlacionar poco entre si.
    """
    return np.sqrt(np.diag(L.T @ np.linalg.inv(R) @ L))


def congruencia(La: np.ndarray, Lb: np.ndarray) -> np.ndarray:
    """Matriz de congruencia de Tucker entre dos soluciones factoriales.

    `phi` es el coseno del angulo entre dos vectores de cargas. Sirve para
    comparar la misma solucion ajustada en dos muestras: por encima de 0.95 se
    leen como equivalentes y entre 0.85 y 0.94 como razonablemente similares.

    Devuelve la matriz completa y no solo la diagonal a proposito. El orden y
    el signo de los factores son arbitrarios y pueden salir distintos en cada
    ajuste, asi que emparejar por posicion produce congruencias absurdamente
    bajas; hay que emparejar por congruencia absoluta maxima.
    """
    na = np.sqrt((La ** 2).sum(0))
    nb = np.sqrt((Lb ** 2).sum(0))
    return (La.T @ Lb) / np.outer(na, nb)
