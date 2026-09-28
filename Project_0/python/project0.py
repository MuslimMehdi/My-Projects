"""Project 0 — live radar dashboard.

Arduino sends: ANGLE,DISTANCE_CM,STATE
Example: 92,34.7,PROXIMITY
"""

from __future__ import annotations

import math
import sys
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime

import serial
from serial.tools import list_ports
from PySide6.QtCore import QPointF, QRectF, QTimer, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

# ---------------- Configuration ----------------
DEFAULT_PORT = "COM3"
BAUD_RATE = 115200
MAX_RANGE_CM = 200.0
PROXIMITY_CM = 50.0
DANGER_CM = 20.0
HISTORY_SIZE = 181
LOG_SIZE = 12
TARGET_TIMEOUT_S = 3.0

BG = QColor("#05090B")
PANEL = QColor("#071116")
PANEL_2 = QColor("#09151A")
GRID = QColor("#0C4D59")
GRID_DIM = QColor("#0A2930")
CYAN = QColor("#20E0D0")
CYAN_DIM = QColor("#167D83")
GREEN = QColor("#2BE38A")
YELLOW = QColor("#FFC642")
RED = QColor("#FF4545")
WHITE = QColor("#DCECEF")
MUTED = QColor("#6F969E")


@dataclass
class Measurement:
    angle: int
    distance: float
    state: str
    timestamp: float


class RadarWidget(QWidget):
    """Custom HUD renderer using QPainter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(500, 500)
        self.angle = 90
        self.distance = -1.0
        self.state = "CLEAR"
        self.points: dict[int, Measurement] = {}
        self.history: deque[Measurement] = deque(maxlen=500)
        self.logs: deque[str] = deque(maxlen=LOG_SIZE)
        self.connected = False
        self.start_time = time.monotonic()
        self.serial_port = "—"
        self.last_packet = 0.0
        self.sweep_phase = 0.0

    @staticmethod
    def status_color(state: str) -> QColor:
        return {"DANGER": RED, "PROXIMITY": YELLOW}.get(state, GREEN)

    def add_measurement(self, m: Measurement) -> None:
        self.angle = m.angle
        self.distance = m.distance
        self.state = m.state
        self.last_packet = m.timestamp
        self.history.append(m)
        if m.distance >= 0:
            self.points[m.angle] = m
        else:
            self.points.pop(m.angle, None)

        stamp = datetime.fromtimestamp(m.timestamp).strftime("%H:%M:%S")
        distance = "----" if m.distance < 0 else f"{m.distance:5.1f}"
        self.logs.appendleft(f"{stamp}   {m.angle:03d}°   {distance} cm   {m.state}")
        self.update()

    def clear_scan(self) -> None:
        self.points.clear()
        self.history.clear()
        self.logs.clear()
        self.update()

    def _polar(self, center: QPointF, radius: float, angle: float, distance: float) -> QPointF:
        r = max(0.0, min(distance, MAX_RANGE_CM)) / MAX_RANGE_CM * radius
        rad = math.radians(angle)
        # 0° left, 90° up, 180° right.
        return QPointF(center.x() - math.cos(rad) * r, center.y() - math.sin(rad) * r)

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), PANEL)

        w, h = self.width(), self.height()
        center = QPointF(w * 0.5, h * 0.56)
        radius = min(w * 0.46, h * 0.42)

        # Outer panel line.
        p.setPen(QPen(GRID, 1))
        p.drawRect(QRectF(0.5, 0.5, w - 1, h - 1))

        # Radar range rings.
        for cm in (50, 100, 150, 200):
            rr = radius * cm / MAX_RANGE_CM
            pen = QPen(GRID if cm < 200 else CYAN_DIM, 1)
            p.setPen(pen)
            p.drawEllipse(center, rr, rr)
            p.setFont(QFont("Consolas", 8))
            p.setPen(MUTED)
            p.drawText(QPointF(center.x() + 6, center.y() - rr + 12), f"{cm} cm")

        # Radial grid.
        p.setPen(QPen(GRID_DIM, 1))
        for angle in range(0, 181, 15):
            q = self._polar(center, radius, angle, MAX_RANGE_CM)
            p.drawLine(center, q)

        # Crosshair.
        p.setPen(QPen(CYAN_DIM, 1))
        p.drawLine(QPointF(center.x() - radius, center.y()), QPointF(center.x() + radius, center.y()))
        p.drawLine(QPointF(center.x(), center.y() - radius), QPointF(center.x(), center.y() + radius))

        # Sweep wedge.
        sweep = self.angle
        end = self._polar(center, radius, sweep, MAX_RANGE_CM)
        wedge = QPolygonF([center])
        for offset in range(-5, 6):
            wedge.append(self._polar(center, radius, sweep + offset, MAX_RANGE_CM))
        p.setBrush(QColor(32, 224, 208, 28))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPolygon(wedge)
        p.setPen(QPen(CYAN, 2))
        p.drawLine(center, end)

        # Target points.
        for m in list(self.points.values()):
            if time.monotonic() - m.timestamp > TARGET_TIMEOUT_S:
                continue
            if m.distance < 0 or m.distance > MAX_RANGE_CM:
                continue
            q = self._polar(center, radius, m.angle, m.distance)
            c = self.status_color(m.state)
            p.setPen(QPen(c, 1))
            p.setBrush(QColor(c.red(), c.green(), c.blue(), 45))
            p.drawEllipse(q, 8, 8)
            p.setBrush(c)
            p.drawEllipse(q, 3.5, 3.5)

        # Center marker.
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(CYAN)
        p.drawEllipse(center, 5, 5)

        # Degree labels.
        p.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        for a, label in ((0, "0°"), (30, "30°"), (60, "60°"), (90, "90°"), (120, "120°"), (150, "150°"), (180, "180°")):
            q = self._polar(center, radius + 22, a, MAX_RANGE_CM)
            p.setPen(WHITE)
            p.drawText(q, label)

        # Header.
        p.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        p.setPen(CYAN)
        p.drawText(18, 26, "RADAR SCAN // LIVE")
        p.setFont(QFont("Consolas", 9))
        p.setPen(MUTED)
        p.drawText(18, 45, "HC-SR04 / 5G SERVO / 180° SWEEP")


class Project0Window(QMainWindow):
    def __init__(self, port: str):
        super().__init__()
        self.setWindowTitle("Project 0 — Radar System")
        self.resize(1500, 900)
        self.setMinimumSize(1100, 700)
        self.setStyleSheet("QMainWindow { background: #05090B; }")

        self.port = port
        self.serial: serial.Serial | None = None
        self.last_error = ""
        self.packet_count = 0
        self.boot_time = time.monotonic()
        self.last_fps_time = time.monotonic()
        self.fps_packets = 0
        self.packet_fps = 0.0
        self.objects: dict[int, Measurement] = {}

        # RadarWidget is retained as the data/rendering model; the HUD is painted
        # directly by HudWindow so the application has a single coherent dashboard.
        self.radar = RadarWidget()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_cycle)
        self.timer.start(16)  # ~60 Hz UI

        self.serial_timer = QTimer(self)
        self.serial_timer.timeout.connect(self.read_serial)
        self.serial_timer.start(5)

        self.open_serial()

    def open_serial(self) -> None:
        try:
            self.serial = serial.Serial(self.port, BAUD_RATE, timeout=0.01)
            time.sleep(1.8)
            self.serial.reset_input_buffer()
            self.radar.connected = True
            self.radar.serial_port = self.port
        except serial.SerialException as exc:
            self.serial = None
            self.last_error = str(exc)
            self.radar.connected = False
            self.radar.serial_port = self.port

    def read_serial(self) -> None:
        if not self.serial or not self.serial.is_open:
            return

        try:
            while self.serial.in_waiting:
                raw = self.serial.readline().decode("utf-8", errors="ignore").strip()
                if not raw or raw.startswith("RADAR"):
                    continue

                parts = raw.split(",")
                if len(parts) != 3:
                    continue

                angle = int(parts[0])
                distance = float(parts[1])
                state = parts[2].strip().upper()

                if not (0 <= angle <= 180):
                    continue
                if state not in {"CLEAR", "PROXIMITY", "DANGER"}:
                    continue
                if distance != -1 and not (0 < distance <= 400):
                    continue

                now = time.time()
                m = Measurement(angle, distance, state, now)
                self.radar.add_measurement(m)
                self.objects[angle] = m
                self.packet_count += 1
                self.fps_packets += 1
        except (ValueError, UnicodeError, serial.SerialException) as exc:
            self.last_error = str(exc)
            if isinstance(exc, serial.SerialException):
                self.close_serial()

    def close_serial(self) -> None:
        if self.serial:
            try:
                self.serial.close()
            except serial.SerialException:
                pass
        self.serial = None
        self.radar.connected = False

    def update_cycle(self) -> None:
        now = time.monotonic()
        if now - self.last_fps_time >= 1.0:
            self.packet_fps = self.fps_packets / (now - self.last_fps_time)
            self.fps_packets = 0
            self.last_fps_time = now
        self.radar.sweep_phase = now
        self.radar.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)

    def closeEvent(self, event) -> None:
        self.close_serial()
        event.accept()


# A separate HUD overlay is used so the radar remains a clean custom widget.
class HudWindow(Project0Window):
    def paintEvent(self, _event) -> None:
        # Paint over the central radar with a full dashboard layout.
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), BG)

        w, h = self.width(), self.height()
        self._draw_dashboard(p, w, h)
        p.end()

    def _panel(self, p, rect: QRectF, title: str) -> None:
        p.setPen(QPen(GRID, 1))
        p.setBrush(PANEL)
        p.drawRoundedRect(rect, 7, 7)
        p.setPen(CYAN)
        p.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        p.drawText(rect.x() + 14, rect.y() + 22, title)
        p.setPen(QPen(GRID_DIM, 1))
        p.drawLine(rect.x() + 10, rect.y() + 31, rect.right() - 10, rect.y() + 31)

    def _dot(self, p, x, y, color, radius=5) -> None:
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        p.drawEllipse(QPointF(x, y), radius, radius)

    def _text(self, p, x, y, text, color=WHITE, size=10, bold=False) -> None:
        p.setPen(color)
        p.setFont(QFont("Consolas", size, QFont.Weight.Bold if bold else QFont.Weight.Normal))
        p.drawText(x, y, text)

    def _draw_dashboard(self, p, w, h):
        # Header
        self._text(p, 24, 32, "PROJECT 0", CYAN, 17, True)
        self._text(p, 155, 32, "RADAR SYSTEM", WHITE, 13, True)
        self._text(p, w - 355, 32, "EXPLORE  /  CREATE  /  TRANSFORM", MUTED, 9, True)
        p.setPen(QPen(GRID, 1))
        p.drawLine(18, 48, w - 18, 48)

        # Header status indicators.
        statuses = [("ON", GREEN), ("PROXIMITY", YELLOW), ("DANGER", RED)]
        sx = w - 520
        for label, color in statuses:
            self._dot(p, sx, 28, color, 5)
            self._text(p, sx + 12, 32, label, color, 9, True)
            sx += 100 if label != "PROXIMITY" else 120

        left = QRectF(18, 62, 245, h - 82)
        center = QRectF(273, 62, w - 620, h - 82)
        right = QRectF(w - 335, 62, 317, h - 82)

        # Left panels
        live = QRectF(left.x(), left.y(), left.width(), 170)
        leds = QRectF(left.x(), left.y() + 182, left.width(), 175)
        log = QRectF(left.x(), left.y() + 369, left.width(), 250)
        system = QRectF(left.x(), left.y() + 632, left.width(), left.height() - 632)
        for rect, title in ((live, "LIVE DATA"), (leds, "LED STATUS"), (log, "SERIAL LOG"), (system, "SYSTEM")):
            self._panel(p, rect, title)

        self._text(p, live.x() + 16, live.y() + 62, "ANGLE", CYAN, 10, True)
        self._text(p, live.x() + 125, live.y() + 62, f"{self.radar.angle:03d}°", WHITE, 17, True)
        d = "----" if self.radar.distance < 0 else f"{self.radar.distance:05.1f} cm"
        self._text(p, live.x() + 16, live.y() + 96, "DISTANCE", CYAN, 10, True)
        self._text(p, live.x() + 125, live.y() + 96, d, self.radar.status_color(self.radar.state), 14, True)
        self._text(p, live.x() + 16, live.y() + 130, "STATUS", CYAN, 10, True)
        self._text(p, live.x() + 125, live.y() + 130, self.radar.state, self.radar.status_color(self.radar.state), 11, True)

        for i, (label, color, active) in enumerate([
            ("SYSTEM ON", GREEN, self.radar.connected),
            ("PROXIMITY", YELLOW, self.radar.state == "PROXIMITY"),
            ("DANGER", RED, self.radar.state == "DANGER"),
        ]):
            yy = leds.y() + 62 + i * 32
            self._dot(p, leds.x() + 23, yy - 4, color if active else MUTED, 6)
            self._text(p, leds.x() + 40, yy, label, color if active else MUTED, 10, True)

        for i, line in enumerate(list(self.radar.logs)[:8]):
            color = RED if "DANGER" in line else YELLOW if "PROXIMITY" in line else GREEN
            self._text(p, log.x() + 12, log.y() + 56 + i * 22, line, color, 8)

        self._text(p, system.x() + 14, system.y() + 57, f"PORT     {self.port}", WHITE, 9)
        self._text(p, system.x() + 14, system.y() + 80, f"BAUD     {BAUD_RATE}", WHITE, 9)
        self._text(p, system.x() + 14, system.y() + 103, f"PACKETS  {self.packet_count}", WHITE, 9)
        self._text(p, system.x() + 14, system.y() + 126, f"RATE     {self.packet_fps:04.1f} Hz", WHITE, 9)

        # Center radar area and bottom graph.
        radar_area = QRectF(center.x(), center.y(), center.width(), max(360, center.height() - 220))
        self._draw_radar(p, radar_area)

        graph = QRectF(center.x(), center.bottom() - 205, center.width(), 205)
        self._draw_graph(p, graph)

        # Right panels.
        objects = QRectF(right.x(), right.y(), right.width(), 320)
        cloud = QRectF(right.x(), right.y() + 332, right.width(), 285)
        legend = QRectF(right.x(), right.y() + 629, right.width(), right.height() - 629)
        self._panel(p, objects, "DETECTED OBJECTS")
        self._panel(p, cloud, "SCAN / POINT CLOUD")
        self._panel(p, legend, "RANGE STATUS")

        self._draw_objects(p, objects)
        self._draw_cloud(p, cloud)
        self._draw_legend(p, legend)

    def _draw_radar(self, p, rect: QRectF):
        # Use a temporary logical center in the dashboard's center panel.
        cx = rect.center().x()
        cy = rect.top() + rect.height() * 0.43
        radius = min(rect.width() * 0.45, rect.height() * 0.38)
        center = QPointF(cx, cy)

        # Border.
        p.setPen(QPen(GRID, 1))
        p.setBrush(PANEL)
        p.drawRoundedRect(rect, 7, 7)
        self._text(p, rect.x() + 14, rect.y() + 22, "RAD_SCAN", CYAN, 10, True)

        for cm in (50, 100, 150, 200):
            rr = radius * cm / MAX_RANGE_CM
            p.setPen(QPen(GRID if cm < 200 else CYAN_DIM, 1))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(center, rr, rr)
            self._text(p, cx + 7, cy - rr + 10, f"{cm} cm", MUTED, 8)

        p.setPen(QPen(GRID_DIM, 1))
        for a in range(0, 181, 15):
            rad = math.radians(a)
            q = QPointF(cx - math.cos(rad) * radius, cy - math.sin(rad) * radius)
            p.drawLine(center, q)

        p.setPen(QPen(CYAN_DIM, 1))
        p.drawLine(cx - radius, cy, cx + radius, cy)
        p.drawLine(cx, cy - radius, cx, cy + radius)

        # Sweep wedge.
        sweep = self.radar.angle
        poly = QPolygonF([center])
        for a in range(sweep - 7, sweep + 8):
            rad = math.radians(a)
            poly.append(QPointF(cx - math.cos(rad) * radius, cy - math.sin(rad) * radius))
        p.setBrush(QColor(32, 224, 208, 28))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPolygon(poly)
        rad = math.radians(sweep)
        q = QPointF(cx - math.cos(rad) * radius, cy - math.sin(rad) * radius)
        p.setPen(QPen(CYAN, 2))
        p.drawLine(center, q)

        # Targets.
        now = time.time()
        for m in self.radar.points.values():
            if now - m.timestamp > TARGET_TIMEOUT_S or m.distance <= 0 or m.distance > MAX_RANGE_CM:
                continue
            rr = radius * m.distance / MAX_RANGE_CM
            ar = math.radians(m.angle)
            pt = QPointF(cx - math.cos(ar) * rr, cy - math.sin(ar) * rr)
            color = self.radar.status_color(m.state)
            p.setPen(QPen(color, 1))
            p.setBrush(QColor(color.red(), color.green(), color.blue(), 35))
            p.drawEllipse(pt, 9, 9)
            p.setBrush(color)
            p.drawEllipse(pt, 4, 4)

        p.setBrush(CYAN)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(center, 5, 5)

        self._text(p, cx - 16, cy + radius + 20, "180°", WHITE, 8)
        self._text(p, cx - 8, cy - radius - 12, "90°", WHITE, 8)
        self._text(p, cx - radius - 26, cy + 4, "0°", WHITE, 8)

    def _draw_objects(self, p, rect):
        self._text(p, rect.x() + 12, rect.y() + 55, "#    ANGLE     DISTANCE     STATUS", MUTED, 8, True)
        now = time.time()
        active = [m for m in self.radar.points.values() if now - m.timestamp <= TARGET_TIMEOUT_S and m.distance > 0]
        active.sort(key=lambda m: m.angle)
        for i, m in enumerate(active[:9], 1):
            yy = rect.y() + 80 + (i - 1) * 25
            c = self.radar.status_color(m.state)
            self._dot(p, rect.x() + 17, yy - 4, c, 4)
            self._text(p, rect.x() + 30, yy, f"{i:02d}", WHITE, 8)
            self._text(p, rect.x() + 66, yy, f"{m.angle:03d}°", WHITE, 8)
            self._text(p, rect.x() + 135, yy, f"{m.distance:6.1f} cm", WHITE, 8)
            self._text(p, rect.x() + 230, yy, m.state, c, 8, True)

    def _draw_cloud(self, p, rect):
        area = QRectF(rect.x() + 12, rect.y() + 48, rect.width() - 24, rect.height() - 62)
        p.setPen(QPen(GRID_DIM, 1))
        for i in range(1, 8):
            x = area.left() + area.width() * i / 8
            p.drawLine(x, area.top(), x, area.bottom())
        for i in range(1, 6):
            y = area.top() + area.height() * i / 6
            p.drawLine(area.left(), y, area.right(), y)

        # Project polar scan points into a pseudo-3D perspective surface.
        now = time.time()
        for m in self.radar.points.values():
            if now - m.timestamp > TARGET_TIMEOUT_S or m.distance <= 0:
                continue
            xnorm = (m.angle - 90) / 90
            znorm = min(m.distance, MAX_RANGE_CM) / MAX_RANGE_CM
            x = area.center().x() + xnorm * area.width() * 0.43
            y = area.bottom() - znorm * area.height() * 0.8
            c = self.radar.status_color(m.state)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(c.red(), c.green(), c.blue(), 170))
            p.drawEllipse(QPointF(x, y), 3, 3)

        self._text(p, area.right() - 95, area.top() + 16, "DISTANCE cm", MUTED, 7)

    def _draw_graph(self, p, rect):
        self._panel(p, rect, "DISTANCE OVER ANGLE")
        area = QRectF(rect.x() + 42, rect.y() + 48, rect.width() - 58, rect.height() - 78)
        p.setPen(QPen(GRID_DIM, 1))
        for i in range(1, 5):
            y = area.bottom() - area.height() * i / 4
            p.drawLine(area.left(), y, area.right(), y)
        for i in range(0, 7):
            x = area.left() + area.width() * i / 6
            p.drawLine(x, area.top(), x, area.bottom())
        self._text(p, area.left() - 36, area.bottom() + 4, "0", MUTED, 7)
        self._text(p, area.left() - 34, area.top() + 5, "200", MUTED, 7)

        by_angle = {m.angle: m for m in self.radar.history}
        pts = []
        for a in range(181):
            m = by_angle.get(a)
            if not m or m.distance < 0:
                continue
            x = area.left() + area.width() * a / 180
            y = area.bottom() - area.height() * min(m.distance, MAX_RANGE_CM) / MAX_RANGE_CM
            pts.append(QPointF(x, y))
        if len(pts) >= 2:
            p.setPen(QPen(CYAN, 1.5))
            p.drawPolyline(QPolygonF(pts))

        for a, label in ((0, "0°"), (60, "60°"), (120, "120°"), (180, "180°")):
            x = area.left() + area.width() * a / 180
            self._text(p, x - 8, area.bottom() + 18, label, MUTED, 7)

    def _draw_legend(self, p, rect):
        items = [("CLEAR", "> 50 cm", GREEN), ("PROXIMITY", "21–50 cm", YELLOW), ("DANGER", "≤ 20 cm", RED)]
        for i, (name, threshold, c) in enumerate(items):
            y = rect.y() + 62 + i * 28
            self._dot(p, rect.x() + 20, y - 4, c, 5)
            self._text(p, rect.x() + 35, y, name, c, 8, True)
            self._text(p, rect.x() + 155, y, threshold, WHITE, 8)
        self._text(p, rect.right() - 145, rect.bottom() - 16, "HC-SR04 / SERVO: 5G", MUTED, 7, True)


def find_default_port() -> str:
    ports = list(list_ports.comports())
    for port in ports:
        description = (port.description or "").lower()
        manufacturer = (port.manufacturer or "").lower()
        if "arduino" in description or "arduino" in manufacturer or "usb serial" in description:
            return port.device
    return DEFAULT_PORT


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Project 0")
    app.setStyle("Fusion")

    port = sys.argv[1] if len(sys.argv) > 1 else find_default_port()
    window = HudWindow(port)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
