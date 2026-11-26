"""Background BLE bridge for pre-shot IMU trajectory tracking."""
from __future__ import annotations
import asyncio
import csv
import logging
import sys
import threading
import time
import numpy as np

DEVICE_NAME = "P8X-BLE"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

# Orientation physique sur le P8X
AXE_HORIZONTAL = "gz"
AXE_VERTICAL = "gx"
INVERT_X = 1
INVERT_Y = 1
MODE_HAUTE_PRECISION_ISM330 = True


class IMUBridge:
    def __init__(self, on_shot_callback=None):
        self.on_shot_callback = on_shot_callback
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self.connected = False
        self.enabled = False
        self._loop = None
        self._task = None
        self._control_lock = threading.Lock()
        self.latest_shot: dict | None = None

    def start(self):
        with self._control_lock:
            if self._thread and self._thread.is_alive():
                if self.enabled:
                    return
                raise ValueError("BLE is still stopping; retry shortly.")
            self.enabled = True
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_loop, name="imu-ble-bridge", daemon=True)
            self._thread.start()

    def stop(self):
        with self._control_lock:
            self.enabled = False
            self._stop_event.set()
            loop, task = self._loop, self._task
            if loop and task:
                try:
                    loop.call_soon_threadsafe(task.cancel)
                except RuntimeError:
                    pass
            if self._thread:
                self._thread.join(timeout=3.0)
            with self._lock:
                self.latest_shot = None

    def get_latest_shot(self) -> dict | None:
        with self._lock:
            return dict(self.latest_shot) if self.latest_shot else None

    def _run_loop(self):
        # Indispensable sur Windows pour que bleak/WinRT fonctionne dans un thread secondaire
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.ole32.CoInitializeEx(None, 0) # COINIT_MULTITHREADED
            except Exception as exc:
                logging.warning("IMU BLE CoInitializeEx warning: %s", exc)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            self._loop = loop
            self._task = loop.create_task(self._ble_worker())
            loop.run_until_complete(self._task)
        except asyncio.CancelledError:
            pass
        except Exception:
            logging.exception("IMU BLE worker crashed")
        finally:
            self.connected = False
            self._task = None
            self._loop = None
            loop.close()

    async def _ble_worker(self):
        try:
            from bleak import BleakScanner, BleakClient
        except ImportError as exc:
            logging.error("IMU BLE disabled: bleak is not installed in this Python (%s) -> %s", sys.executable, exc)
            return

        logging.info("IMU BLE worker scanning for '%s'...", DEVICE_NAME)

        while not self._stop_event.is_set():
            try:
                devices = await BleakScanner.discover(timeout=4.0)
                target = next((d for d in devices if d.name and DEVICE_NAME.lower() in d.name.lower()), None)

                if not target:
                    await asyncio.sleep(1.5)
                    continue

                logging.info("IMU BLE found '%s' (%s), connecting...", target.name, target.address)
                async with BleakClient(target, timeout=10.0) as client:
                    self.connected = True
                    logging.info("IMU BLE connected to %s!", target.name)
                    buffer_text = ""
                    receiving = False

                    def handle_rx(_, data: bytearray):
                        nonlocal buffer_text, receiving
                        chunk = data.decode("utf-8", errors="ignore")
                        if "START_SHOT" in chunk:
                            receiving = True
                            buffer_text = chunk.split("START_SHOT", 1)[1]
                            return
                        if receiving:
                            if "END_SHOT" in chunk:
                                buffer_text += chunk.split("END_SHOT", 1)[0]
                                receiving = False
                                self._process_csv(buffer_text)
                                buffer_text = ""
                            else:
                                buffer_text += chunk

                    await client.start_notify(UART_TX_CHAR_UUID, handle_rx)
                    while client.is_connected and not self._stop_event.is_set():
                        await asyncio.sleep(0.25)

                logging.info("IMU BLE disconnected from %s", target.name)
            except Exception as exc:
                logging.warning("IMU BLE connection cycle error: %s", exc)
            finally:
                self.connected = False
                if not self._stop_event.is_set():
                    await asyncio.sleep(1.5)

    def _process_csv(self, csv_text: str):
        temps, gx, gy, gz = [], [], [], []
        for row in csv.reader(csv_text.strip().splitlines()):
            if len(row) != 4 or row[0] == "Temps_ms":
                continue
            try:
                t_val, gx_val, gy_val, gz_val = row
                temps.append(float(t_val))
                gx.append(float(gx_val))
                gy.append(float(gy_val))
                gz.append(float(gz_val))
            except ValueError:
                continue

        if len(temps) < 15:
            return

        axes = {"gx": np.array(gx), "gy": np.array(gy), "gz": np.array(gz)}
        t_sec = np.array(temps) / 1000.0
        dt = np.diff(t_sec, prepend=t_sec[0])

        x_mm = np.cumsum(axes[AXE_HORIZONTAL] * dt * 10000.0) * INVERT_X
        y_mm = np.cumsum(axes[AXE_VERTICAL] * dt * 10000.0) * INVERT_Y
        x_mm -= x_mm[-1]
        y_mm -= y_mm[-1]

        dx, dy = np.diff(x_mm), np.diff(y_mm)
        dist = np.hypot(dx, dy)
        l1 = float(np.sum(dist))
        idx_200 = int(len(x_mm) * 0.8)
        l02 = float(np.sum(dist[idx_200:]))

        dt_safe = np.where(np.diff(t_sec) <= 0, 1e-4, np.diff(t_sec))
        vitesses = dist / dt_safe
        idx_100 = int(len(vitesses) * 0.9)
        vit_fin = vitesses[idx_100:-1] if len(vitesses) > idx_100 + 2 else vitesses[idx_100:]
        pic_fin = float(np.max(vit_fin)) if len(vit_fin) > 0 else 0.0
        dep_net = float(np.hypot(x_mm[-2] - x_mm[idx_100], y_mm[-2] - y_mm[idx_100]))

        seuil_pic = 60.0 if MODE_HAUTE_PRECISION_ISM330 else 80.0
        seuil_dep = 3.5 if MODE_HAUTE_PRECISION_ISM330 else 4.5
        coup_de_doigt = bool(pic_fin > seuil_pic and dep_net > seuil_dep)

        step = max(1, len(x_mm) // 100)
        points = [
            {"x": round(float(x_mm[i]), 2), "y": round(float(y_mm[i]), 2), "t": round(float(temps[i]), 1)}
            for i in range(0, len(x_mm), step)
        ]
        if (len(x_mm)-1) % step != 0:
            points.append({"x": 0.0, "y": 0.0, "t": round(float(temps[-1]), 1)})

        shot_payload = {
            "timestamp": time.time(),
            "l1_mm": round(l1, 1),
            "l02_mm": round(l02, 1),
            "coup_de_doigt": coup_de_doigt,
            "pic_vitesse_mms": round(pic_fin, 0),
            "points": points,
        }

        with self._lock:
            if self._stop_event.is_set():
                return
            self.latest_shot = shot_payload

        logging.info("IMU shot processed: L1=%.1fmm, L0.2=%.1fmm, flinch=%s", l1, l02, coup_de_doigt)
        if self.on_shot_callback:
            self.on_shot_callback(shot_payload)
