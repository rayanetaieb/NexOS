def test_opencv_pipeline():
    import cv2
    import numpy as np
    img = np.zeros((100, 100, 3), np.uint8)
    cv2.rectangle(img, (20, 20), (80, 80), (255, 255, 255), -1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    assert len(contours) == 1 and abs(cv2.contourArea(contours[0]) - 3600) < 50


def test_pillow_roundtrip(tmp_path):
    from PIL import Image
    p = tmp_path / "a.png"
    Image.new("RGB", (32, 16), "blue").save(p)
    assert Image.open(p).size == (32, 16)


def test_yolo_builds_and_infers_offline():
    """Construit un YOLO depuis sa config (sans télécharger de poids) et fait une inférence."""
    import numpy as np
    from ultralytics import YOLO
    model = YOLO("yolov8n.yaml")
    res = model.predict(np.zeros((320, 320, 3), np.uint8), imgsz=320, verbose=False)
    assert len(res) == 1
