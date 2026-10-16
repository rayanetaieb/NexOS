import matplotlib
matplotlib.use("Agg")


def test_numpy_scipy_linear_algebra():
    import numpy as np
    from scipy import linalg, integrate
    a = np.array([[3.0, 1.0], [1.0, 2.0]])
    x = linalg.solve(a, [9.0, 8.0])
    assert np.allclose(x, [2.0, 3.0])
    val, _ = integrate.quad(lambda t: t**2, 0, 3)
    assert abs(val - 9.0) < 1e-9


def test_pandas_groupby():
    import pandas as pd
    df = pd.DataFrame({"g": ["a", "b", "a"], "v": [1, 2, 3]})
    assert df.groupby("g")["v"].sum().to_dict() == {"a": 4, "b": 2}


def test_sympy_solve():
    import sympy as sp
    x = sp.symbols("x")
    assert set(sp.solve(x**2 - 4, x)) == {-2, 2}


def test_matplotlib_render(tmp_path):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2], [0, 1, 4])
    out = tmp_path / "f.png"
    fig.savefig(out)
    assert out.stat().st_size > 1000


def test_statsmodels_ols():
    import numpy as np
    import statsmodels.api as sm
    rng = np.random.default_rng(0)
    x = rng.normal(size=200)
    y = 2 * x + 1 + rng.normal(scale=0.01, size=200)
    res = sm.OLS(y, sm.add_constant(x)).fit()
    assert abs(res.params[1] - 2) < 0.01


def test_jupyter_kernel_available():
    from jupyter_client.kernelspec import KernelSpecManager
    import jupyterlab  # noqa: F401
    assert "python3" in KernelSpecManager().find_kernel_specs()
