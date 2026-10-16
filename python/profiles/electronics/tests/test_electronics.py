def test_pyserial_loopback():
    import serial
    s = serial.serial_for_url("loop://", timeout=1)
    s.write(b"NexOS\n")
    assert s.readline() == b"NexOS\n"


def test_pyvisa_py_backend():
    import pyvisa
    rm = pyvisa.ResourceManager("@py")
    assert isinstance(rm.list_resources(), tuple)
    rm.close()


def test_signal_processing():
    import numpy as np
    from scipy import signal
    fs = 1000
    t = np.arange(0, 1, 1 / fs)
    x = np.sin(2 * np.pi * 50 * t) + 0.5 * np.sin(2 * np.pi * 200 * t)
    b, a = signal.butter(4, 100, fs=fs)
    y = signal.filtfilt(b, a, x)
    spec = np.abs(np.fft.rfft(y))
    assert spec[200] < 0.05 * spec[50]


def test_microcontroller_tools_and_usb():
    import esptool, mpremote, pymodbus, usb.core  # noqa: F401,E401
    assert esptool.__version__


def test_pyqtgraph_offscreen(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    import pyqtgraph as pg
    app = pg.mkQApp()
    w = pg.PlotWidget(); w.plot([1, 2, 3])
    assert app is not None
