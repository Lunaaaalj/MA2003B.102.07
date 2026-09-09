"""Pruebas de la maquinaria del analisis factorial.

Las rutinas de src/factorial.py estan escritas a mano porque factor_analyzer
0.5.1 no corre contra scikit-learn 1.9 (ver el docstring del modulo), asi que
conviene amarrarlas con propiedades que se puedan verificar sin la libreria.

    source venv/bin/activate
    pytest tests/test_factorial.py -v
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.factorial import (  # noqa: E402
    ejes_principales,
    oblimin,
    puntajes_bartlett,
    residuos,
    varimax,
)


@pytest.fixture
def modelo_conocido():
    """Datos generados desde un modelo factorial de tres factores conocido.

    Al construir la correlacion desde `LL' + U` sabemos la respuesta de
    antemano, que es lo que permite verificar la recuperacion.
    """
    rng = np.random.default_rng(11)
    p, k = 12, 3
    L = np.zeros((p, k))
    for j in range(k):                       # estructura simple perfecta
        L[j * 4:(j + 1) * 4, j] = [.8, .75, .7, .65]
    u2 = 1 - (L ** 2).sum(1)
    R = L @ L.T + np.diag(u2)
    return L, u2, R, rng


def test_ejes_principales_recupera_comunalidades(modelo_conocido):
    L, u2, R, _ = modelo_conocido
    _, h2 = ejes_principales(R, 3)
    assert np.allclose(h2, 1 - u2, atol=1e-3)


def test_ejes_principales_reproduce_la_correlacion(modelo_conocido):
    _, _, R, _ = modelo_conocido
    Lh, h2 = ejes_principales(R, 3)
    _, rmsr = residuos(R, Lh, h2)
    assert rmsr < 1e-3


def test_varimax_preserva_el_espacio_comun(modelo_conocido):
    """Una rotacion ortogonal no puede cambiar comunalidades ni ajuste."""
    _, _, R, _ = modelo_conocido
    A, _ = ejes_principales(R, 3)
    Lv = varimax(A)
    assert np.allclose(A @ A.T, Lv @ Lv.T, atol=1e-10)


def test_varimax_encuentra_la_estructura_simple(modelo_conocido):
    L, _, R, _ = modelo_conocido
    A, _ = ejes_principales(R, 3)
    Lv = np.abs(varimax(A))
    # cada variable debe cargar en un solo factor: la carga dominante manda
    dominante = Lv.max(1)
    segunda = np.sort(Lv, axis=1)[:, -2]
    assert (dominante > 0.55).all()
    assert (segunda < 0.20).all()
    # y el bloque de cuatro variables debe caer junto en el mismo factor
    grupos = Lv.argmax(1)
    assert len(set(grupos[:4])) == len(set(grupos[4:8])) == 1


def test_oblimin_devuelve_phi_valida(modelo_conocido):
    _, _, R, _ = modelo_conocido
    A, _ = ejes_principales(R, 3)
    _, phi = oblimin(A)
    assert np.allclose(np.diag(phi), 1, atol=1e-8)
    assert np.allclose(phi, phi.T, atol=1e-10)
    assert (np.abs(phi) <= 1 + 1e-8).all()
    assert np.linalg.eigvalsh(phi).min() > 0      # definida positiva


def test_oblimin_sobre_factores_ortogonales_no_los_correlaciona(modelo_conocido):
    """Si los factores verdaderos son ortogonales, phi debe salir casi la identidad."""
    _, _, R, _ = modelo_conocido
    A, _ = ejes_principales(R, 3)
    _, phi = oblimin(A)
    fuera = phi[~np.eye(3, dtype=bool)]
    assert np.abs(fuera).max() < 0.15


def test_puntajes_bartlett_quedan_casi_incorrelados(modelo_conocido):
    L, u2, R, rng = modelo_conocido
    n = 20_000
    F = rng.standard_normal((n, 3))
    Z = F @ L.T + rng.standard_normal((n, 12)) * np.sqrt(u2)
    Z = (Z - Z.mean(0)) / Z.std(0)

    A, h2 = ejes_principales(np.corrcoef(Z, rowvar=False), 3)
    Lv = varimax(A)
    P, W = puntajes_bartlett(Z, Lv, h2)

    assert P.shape == (n, 3)
    vif = np.diag(np.linalg.inv(np.corrcoef(P, rowvar=False)))
    assert (vif < 1.3).all()


def test_puntajes_bartlett_aplican_los_pesos_de_entrenamiento(modelo_conocido):
    """W debe bastar para puntuar datos nuevos sin reajustar el modelo."""
    L, u2, R, rng = modelo_conocido
    Z = rng.standard_normal((500, 12))
    A, h2 = ejes_principales(R, 3)
    P, W = puntajes_bartlett(Z, A, h2)
    assert np.allclose(P, Z @ W.T)


def test_residuos_detecta_un_modelo_insuficiente(modelo_conocido):
    """Pedir menos factores de los que hay debe empeorar el RMSR."""
    _, _, R, _ = modelo_conocido
    _, rmsr3 = residuos(R, *ejes_principales(R, 3))
    _, rmsr1 = residuos(R, *ejes_principales(R, 1))
    assert rmsr1 > rmsr3
