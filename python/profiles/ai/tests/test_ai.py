import os
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")


def test_torch_train_and_export_onnx(tmp_path):
    import numpy as np
    import onnxruntime as ort
    import torch
    torch.manual_seed(0)
    model = torch.nn.Linear(3, 1)
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    x = torch.randn(64, 3); y = x @ torch.tensor([[1.0], [-2.0], [0.5]])
    for _ in range(300):
        opt.zero_grad(); loss = ((model(x) - y) ** 2).mean(); loss.backward(); opt.step()
    assert loss.item() < 1e-3
    path = tmp_path / "m.onnx"
    torch.onnx.export(model, torch.randn(1, 3), path, input_names=["x"], output_names=["y"], dynamo=False)
    sess = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    inp = np.ones((1, 3), dtype=np.float32)
    assert np.allclose(sess.run(None, {"x": inp})[0], model(torch.from_numpy(inp)).detach().numpy(), atol=1e-5)


def test_tensorflow_keras_fit():
    import numpy as np
    import keras
    x = np.linspace(-1, 1, 200).reshape(-1, 1).astype("float32"); y = 3 * x + 1
    m = keras.Sequential([keras.Input((1,)), keras.layers.Dense(1)])
    m.compile(optimizer=keras.optimizers.SGD(0.1), loss="mse")
    m.fit(x, y, epochs=60, verbose=0)
    assert m.evaluate(x, y, verbose=0) < 1e-3


def test_sklearn_xgboost():
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    from xgboost import XGBClassifier
    X, y = load_iris(return_X_y=True)
    a, b, c, d = train_test_split(X, y, random_state=0)
    assert XGBClassifier(n_estimators=30).fit(a, c).score(b, d) > 0.9


def test_gpu_reported_honestly():
    """N'affirme jamais l'usage du GPU : on ne l'annonce que si un calcul réel y réussit."""
    import torch
    if torch.cuda.is_available():
        t = torch.ones(2, device="cuda") * 2
        assert t.sum().item() == 4
    else:
        assert torch.ones(2).sum().item() == 2  # CPU seulement
