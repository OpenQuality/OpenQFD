"""
Welcome / Poster View — shown before any project is open.

Shows a small illustrative House of Quality (roof + room + floor) and
positions the ten-tool flow (VOC/CTQ/HOQ/KANO/AHP/Pareto/TRIZ/FMEA/DOE/DSM)
so each node sits next to the HOQ region it actually interacts with:
Kano/AHP feed the left wall (VOC), TRIZ resolves roof conflicts, Pareto
prioritizes the floor's output, and FMEA/DOE/DSM continue downstream.
"""
import math
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPainterPath, QLinearGradient

from utils.i18n import t


# Sample data purely for the poster illustration (not real project data)
_MOCK_VOCS = ["电池续航", "屏幕清晰", "佩戴舒适", "操作简便"]
_MOCK_CTQS = ["电池容量", "屏幕分辨率", "整机重量", "响应时间"]
_MOCK_REL = {  # (voc_idx, ctq_idx) -> strength 9/3/1
    (0, 0): 9, (0, 2): 3, (1, 1): 9, (1, 3): 3,
    (2, 2): 9, (2, 0): 1, (3, 3): 9, (3, 1): 3,
}
_MOCK_ROOF = {(0, 2): "--", (1, 3): "+"}   # (i,j) -> correlation symbol
_MOCK_TAI = [0.85, 0.55, 0.70, 0.40]        # relative floor bar heights

_REL_SYMBOL = {9: "●", 3: "◎", 1: "△"}
_REL_COLOR = {9: "#D32F2F", 3: "#1565C0", 1: "#757575"}
_ROOF_COLOR = {"++": "#D32F2F", "+": "#FBC02D", "-": "#A5D6A7", "--": "#1B5E20"}

# Satellite tool nodes — (x, y, w, h, title, subtitle i18n key, color), fractions of canvas
_NODES = {
    "kano":   (0.015, 0.14, 0.155, 0.11, "Kano", "welcome.node_kano", "#8E44AD"),
    "ahp":    (0.015, 0.30, 0.155, 0.11, "AHP", "welcome.node_ahp", "#8E44AD"),
    "triz":   (0.83, 0.03, 0.155, 0.105, "TRIZ", "welcome.node_triz", "#16A085"),
    "pareto": (0.365, 0.685, 0.27, 0.105, "Pareto", "welcome.node_pareto", "#27AE60"),
    "fmea":   (0.03, 0.85, 0.20, 0.105, "FMEA", "welcome.node_fmea", "#C0392B"),
    "doe":    (0.40, 0.85, 0.20, 0.105, "DOE", "welcome.node_doe", "#C0392B"),
    "dsm":    (0.77, 0.85, 0.20, 0.105, "DSM", "welcome.node_dsm", "#C0392B"),
}


class PosterCanvas(QWidget):
    """Custom-painted House of Quality mockup + surrounding tool-chain flow."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(460)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._vocs = _MOCK_VOCS
        self._ctqs = _MOCK_CTQS
        self._rel = _MOCK_REL
        self._roof = _MOCK_ROOF
        self._tai = _MOCK_TAI

    def set_real_data(self, vocs, ctqs, rel, roof, tai):
        """Feed the poster real project data (up to 4 VOCs/CTQs) so it shows
        an actual HOQ excerpt instead of the placeholder sample. Pass empty
        vocs/ctqs to fall back to the placeholder (e.g. no project loaded)."""
        if vocs and ctqs:
            self._vocs, self._ctqs = vocs, ctqs
            self._rel, self._roof, self._tai = rel, roof, tai
        else:
            self._vocs, self._ctqs = _MOCK_VOCS, _MOCK_CTQS
            self._rel, self._roof, self._tai = _MOCK_REL, _MOCK_ROOF, _MOCK_TAI
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0, QColor("#F5F9FC"))
        grad.setColorAt(1, QColor("#EBF2F8"))
        painter.fillRect(self.rect(), QBrush(grad))

        hoq_rect = QRectF(0.235 * w, 0.03 * h, 0.53 * w, 0.62 * h)
        anchors = self._draw_hoq_mockup(painter, hoq_rect)

        # Arrows connecting satellite nodes to the HOQ region they act on
        painter.setPen(QPen(QColor("#95A5A6"), 2.0))
        node_rects = {k: self._node_rect(k, w, h) for k in _NODES}
        self._draw_arrow(painter, node_rects["kano"], anchors["left_wall_upper"])
        self._draw_arrow(painter, node_rects["ahp"], anchors["left_wall_lower"])
        self._draw_arrow(painter, node_rects["triz"], anchors["roof_tip"])
        self._draw_arrow(painter, anchors["floor_bottom"], node_rects["pareto"])
        self._draw_arrow(painter, node_rects["pareto"], node_rects["fmea"])
        self._draw_arrow(painter, node_rects["pareto"], node_rects["doe"])
        self._draw_arrow(painter, node_rects["pareto"], node_rects["dsm"])

        for key in _NODES:
            x, y, fw, fh, title, subtitle_key, color = _NODES[key]
            self._draw_node(painter, node_rects[key], title, t(subtitle_key), color)

        painter.end()

    def _node_rect(self, key, w, h):
        x, y, fw, fh, *_ = _NODES[key]
        return QRectF(x * w, y * h, fw * w, fh * h)

    # ── HOQ mockup: roof + room (VOC x CTQ) + floor ────────────────
    def _draw_hoq_mockup(self, painter, rect):
        left_label_w = rect.width() * 0.20
        room_x = rect.x() + left_label_w
        room_w = rect.width() - left_label_w
        nv, nc = len(self._vocs), len(self._ctqs)
        col_w = room_w / nc

        header_h = rect.height() * 0.12
        roof_h = rect.height() * 0.16
        floor_h = rect.height() * 0.12
        room_y = rect.y() + roof_h + header_h
        row_h = (rect.height() - roof_h - header_h - floor_h) / nv

        # -- Roof (flattened diamond grid of CTQ-CTQ correlations) --
        roof_top = rect.y()
        half = col_w / 2.0
        half_y = roof_h * 0.42
        for i in range(nc):
            for j in range(i + 1, nc):
                cx = room_x + (i + j + 1) / 2.0 * col_w
                cy = room_y - (j - i) * half_y
                sym = self._roof.get((i, j))
                color = QColor(_ROOF_COLOR.get(sym, "#F5F5F5"))
                diamond = QPainterPath()
                diamond.moveTo(cx, cy - half_y)
                diamond.lineTo(cx + half, cy)
                diamond.lineTo(cx, cy + half_y)
                diamond.lineTo(cx - half, cy)
                diamond.closeSubpath()
                painter.setBrush(QBrush(color))
                painter.setPen(QPen(QColor("#BDBDBD"), 0.6))
                painter.drawPath(diamond)
                if sym:
                    painter.setPen(QPen(Qt.white if sym in ("++", "--") else QColor("#333")))
                    f = painter.font(); f.setPointSize(7); f.setBold(True)
                    painter.setFont(f)
                    painter.drawText(QRectF(cx - half, cy - half_y, col_w, 2 * half_y),
                                      Qt.AlignCenter, sym)
        roof_tip = QPointF(room_x + room_w / 2.0, roof_top)

        # -- CTQ column headers --
        painter.setPen(QPen(QColor("#1B5E8C")))
        f = painter.font(); f.setPointSize(7); f.setBold(True)
        painter.setFont(f)
        for j, name in enumerate(self._ctqs):
            cell = QRectF(room_x + j * col_w, room_y - header_h, col_w, header_h)
            painter.drawText(cell, Qt.AlignCenter | Qt.TextWordWrap, name)

        # -- Room grid + VOC row labels --
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.setPen(QPen(QColor("#D5DBE1"), 1))
        painter.drawRect(QRectF(room_x, room_y, room_w, row_h * nv))
        for i in range(nv):
            y = room_y + i * row_h
            painter.setPen(QPen(QColor("#D5DBE1"), 1))
            painter.drawLine(QPointF(room_x, y), QPointF(room_x + room_w, y))
            label_rect = QRectF(rect.x(), y, left_label_w - 4, row_h)
            painter.setPen(QPen(QColor("#2C3E50")))
            lf = painter.font(); lf.setPointSize(7); lf.setBold(False)
            painter.setFont(lf)
            painter.drawText(label_rect, Qt.AlignVCenter | Qt.AlignRight, self._vocs[i])
            for j in range(nc):
                x = room_x + j * col_w
                painter.drawLine(QPointF(x, room_y), QPointF(x, room_y + row_h * nv))
                strength = self._rel.get((i, j))
                if strength:
                    painter.setPen(QPen(QColor(_REL_COLOR[strength])))
                    sf = painter.font(); sf.setPointSize(11); sf.setBold(True)
                    painter.setFont(sf)
                    painter.drawText(QRectF(x, y, col_w, row_h), Qt.AlignCenter, _REL_SYMBOL[strength])

        left_wall_x = rect.x() + left_label_w * 0.55
        left_wall_upper = QPointF(left_wall_x, room_y + row_h * 1.0)
        left_wall_lower = QPointF(left_wall_x, room_y + row_h * 3.0)

        # -- Floor: Tai bars --
        floor_y = room_y + row_h * nv
        painter.setPen(QPen(QColor("#1B5E8C")))
        ff = painter.font(); ff.setPointSize(7); ff.setBold(True)
        painter.setFont(ff)
        painter.drawText(QRectF(rect.x(), floor_y, left_label_w - 4, floor_h),
                          Qt.AlignVCenter | Qt.AlignRight, "Tai")
        max_bar_h = floor_h * 0.72
        for j, val in enumerate(self._tai):
            bar_h = max_bar_h * val
            bar_rect = QRectF(room_x + j * col_w + col_w * 0.22,
                               floor_y + floor_h - bar_h - floor_h * 0.12,
                               col_w * 0.56, bar_h)
            painter.setBrush(QBrush(QColor("#FFD54F")))
            painter.setPen(QPen(QColor("#F9A825"), 0.8))
            painter.drawRect(bar_rect)
        floor_bottom = QPointF(room_x + room_w / 2.0, floor_y + floor_h)

        # -- HOQ label badge over the room --
        painter.setPen(QPen(QColor("#E67E22"), 2))
        painter.setBrush(QBrush(QColor(230, 126, 34, 40)))
        painter.drawRoundedRect(QRectF(room_x + room_w * 0.30, room_y + row_h * nv * 0.38,
                                        room_w * 0.40, row_h * 1.1), 6, 6)
        painter.setPen(QPen(QColor("#E67E22")))
        hf = painter.font(); hf.setPointSize(9); hf.setBold(True)
        painter.setFont(hf)
        painter.drawText(QRectF(room_x + room_w * 0.30, room_y + row_h * nv * 0.38,
                                 room_w * 0.40, row_h * 1.1), Qt.AlignCenter, t("welcome.hoq_badge"))

        return {
            "roof_tip": roof_tip,
            "left_wall_upper": left_wall_upper,
            "left_wall_lower": left_wall_lower,
            "floor_bottom": floor_bottom,
        }

    # ── Arrows & satellite nodes ────────────────────────────────────
    def _draw_arrow(self, painter, a, b):
        """a, b may be a QRectF (node) or QPointF (anchor on the mockup)."""
        p_from = a.center() if isinstance(a, QRectF) else a
        p_to = b.center() if isinstance(b, QRectF) else b
        p1 = self._edge_point(a, p_to) if isinstance(a, QRectF) else a
        p2 = self._edge_point(b, p_from) if isinstance(b, QRectF) else b
        painter.drawLine(p1, p2)
        angle = math.atan2(p2.y() - p1.y(), p2.x() - p1.x())
        size = 8
        p_left = QPointF(p2.x() - size * math.cos(angle - math.pi / 7),
                          p2.y() - size * math.sin(angle - math.pi / 7))
        p_right = QPointF(p2.x() - size * math.cos(angle + math.pi / 7),
                           p2.y() - size * math.sin(angle + math.pi / 7))
        path = QPainterPath()
        path.moveTo(p2); path.lineTo(p_left); path.lineTo(p_right); path.closeSubpath()
        painter.setBrush(QBrush(QColor("#95A5A6")))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)
        painter.setPen(QPen(QColor("#95A5A6"), 2.0))

    @staticmethod
    def _edge_point(rect, toward):
        cx, cy = rect.center().x(), rect.center().y()
        dx, dy = toward.x() - cx, toward.y() - cy
        if dx == 0 and dy == 0:
            return rect.center()
        hw, hh = rect.width() / 2, rect.height() / 2
        scale = min(abs(hw / dx) if dx else float('inf'),
                     abs(hh / dy) if dy else float('inf'))
        return QPointF(cx + dx * scale, cy + dy * scale)

    def _draw_node(self, painter, rect, title, subtitle, color):
        qcolor = QColor(color)
        painter.setPen(QPen(qcolor.darker(115), 1.3))
        painter.setBrush(QBrush(qcolor))
        painter.drawRoundedRect(rect, 8, 8)

        painter.setPen(QPen(Qt.white))
        title_font = QFont("Microsoft YaHei", 11, QFont.Bold)
        painter.setFont(title_font)
        title_rect = QRectF(rect.x(), rect.y() + rect.height() * 0.14,
                             rect.width(), rect.height() * 0.5)
        painter.drawText(title_rect, Qt.AlignCenter, title)

        sub_font = QFont("Microsoft YaHei", 7.5)
        painter.setFont(sub_font)
        sub_rect = QRectF(rect.x(), rect.y() + rect.height() * 0.56,
                           rect.width(), rect.height() * 0.4)
        painter.drawText(sub_rect, Qt.AlignCenter, subtitle)


class WelcomeView(QWidget):
    """Landing page shown before any project is opened."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(6)

        title = QLabel(t("welcome.title"))
        title.setFont(QFont("Microsoft YaHei", 22, QFont.Bold))
        title.setStyleSheet("color: #1B5E8C;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel(t("welcome.subtitle"))
        subtitle.setStyleSheet("color: #7F8C8D; font-size: 13px;")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.canvas = PosterCanvas()
        layout.addWidget(self.canvas, 1)

        hint = QLabel(t("welcome.hint"))
        hint.setStyleSheet("color: #1B5E8C; font-size: 13px; font-weight: bold; padding: 8px;")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)
