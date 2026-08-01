"""
HOQ (House of Quality) - Integrated View
All 7 regions drawn together: Roof, Ceiling, Left Wall, Room, Right Wall, Floor, Basement.
Reference: Classic WinQFD style with triangle roof and colored relationship blocks.
"""
import math
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QScrollArea, QGroupBox, QSizePolicy,
    QMessageBox, QHeaderView, QAbstractItemView, QFrame, QSplitter
)
from PySide6.QtCore import Qt, Signal, QSize, QRect, QPoint
from PySide6.QtGui import (
    QColor, QFont, QPainter, QBrush, QPen, QPolygon,
    QLinearGradient, QPainterPath, QFontMetrics
)

from engines.compute import HOQEngine
from views.styles import COLORS, DIRECTION_SYMBOLS
from utils.i18n import t


# ── Color constants for relationship blocks ──────────────────────
CLR_STRONG = QColor("#D32F2F")       # red - strong (9)
CLR_MEDIUM = QColor("#1565C0")       # blue - medium (3)
CLR_WEAK   = QColor("#757575")       # gray - weak (1)
CLR_EMPTY  = QColor("#FFFFFF")       # white - none
CLR_ROOF_SP = QColor("#D32F2F")      # red - strong positive
CLR_ROOF_P  = QColor("#FBC02D")      # yellow - positive
CLR_ROOF_N  = QColor("#A5D6A7")      # light green - negative
CLR_ROOF_SN = QColor("#1B5E20")      # dark green - strong negative


STRENGTH_COLORS = {9: CLR_STRONG, 3: CLR_MEDIUM, 1: CLR_WEAK, 0: CLR_EMPTY}
STRENGTH_LABELS = {9: "强相关(9)", 3: "中相关(3)", 1: "弱相关(1)", 0: ""}


# ══════════════════════════════════════════════════════════════════
#  RoofWidget — draws the triangle correlation matrix on top
# ══════════════════════════════════════════════════════════════════
class RoofWidget(QWidget):
    """Custom-painted triangle roof showing CTQ-CTQ correlations."""

    correlation_clicked = Signal(int, int)  # ctq index i, j

    # Vertical compression factor — keeps the roof looking like a shallow,
    # flat pitched roof instead of a tall diamond pyramid. 1.0 = true diamonds.
    FLATTEN = 0.42

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ctq_names = []
        self._corr_data = {}   # {(i,j): str}  i < j
        self._col_centers = [] # x-center of each CTQ column, in this widget's own coordinates
        self._cell_w = 46      # nominal width, only used to size the diamonds themselves
        self.setMinimumHeight(20)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_data(self, ctq_names, corr_data, col_centers, cell_w=46):
        """col_centers: x-center (in this widget's coordinates) of each CTQ column —
        queried from the table's actual columnViewportPosition/columnWidth, so this
        stays correct even if the user manually resizes a column (constant `cell_w`
        would silently drift out of alignment column-by-column otherwise)."""
        self._ctq_names = ctq_names
        self._corr_data = corr_data
        self._col_centers = col_centers
        self._cell_w = cell_w
        n = len(ctq_names)
        h = int(n * self._cell_w * 0.5 * self.FLATTEN) + 20 if n > 0 else 20
        self.setFixedHeight(max(h, 20))
        self.update()

    def paintEvent(self, event):
        if not self._ctq_names or len(self._col_centers) != len(self._ctq_names):
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        n = len(self._ctq_names)
        cw = self._cell_w
        half = cw / 2.0
        half_y = half * self.FLATTEN
        centers = self._col_centers

        # Draw the diamond grid
        for i in range(n):
            for j in range(i + 1, n):
                corr = self._corr_data.get((i, j), "")
                cx = (centers[i] + centers[j]) / 2.0
                cy = self.height() - (j - i) * half_y

                # Draw diamond cell (flattened — wider than tall, like a roof pitch)
                diamond = QPolygon([
                    QPoint(int(cx), int(cy - half_y)),
                    QPoint(int(cx + half), int(cy)),
                    QPoint(int(cx), int(cy + half_y)),
                    QPoint(int(cx - half), int(cy)),
                ])

                # Fill color based on correlation
                if corr == "++":
                    painter.setBrush(QBrush(CLR_ROOF_SP))
                elif corr == "+":
                    painter.setBrush(QBrush(CLR_ROOF_P))
                elif corr == "-":
                    painter.setBrush(QBrush(CLR_ROOF_N))
                elif corr == "--":
                    painter.setBrush(QBrush(CLR_ROOF_SN))
                else:
                    painter.setBrush(QBrush(QColor("#F5F5F5")))

                painter.setPen(QPen(QColor("#BDBDBD"), 0.5))
                painter.drawPolygon(diamond)

                # Draw symbol text
                if corr:
                    painter.setPen(QPen(Qt.white if corr in ("++", "--") else Qt.black))
                    font = painter.font()
                    font.setPointSize(7)
                    font.setBold(True)
                    painter.setFont(font)
                    painter.drawText(QRect(int(cx - half), int(cy - half_y), int(cw), int(2 * half_y)),
                                     Qt.AlignCenter, corr)

        # Draw legend
        painter.setPen(QPen(Qt.black))
        font = painter.font()
        font.setPointSize(8)
        font.setBold(False)
        painter.setFont(font)

        lx = self.width() - 180
        ly = 8
        legends = [
            (CLR_ROOF_SP, t("hoq.roof_legend_sp")),
            (CLR_ROOF_P,  t("hoq.roof_legend_p")),
            (CLR_ROOF_N,  t("hoq.roof_legend_n")),
            (CLR_ROOF_SN, t("hoq.roof_legend_sn")),
        ]
        for color, text in legends:
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor("#BDBDBD"), 0.5))
            painter.drawRect(lx, ly, 14, 14)
            painter.setPen(QPen(Qt.black))
            painter.drawText(lx + 20, ly + 12, text)
            ly += 18

        painter.end()

    def mousePressEvent(self, event):
        """Handle click to cycle roof correlation."""
        if not self._ctq_names or len(self._col_centers) != len(self._ctq_names):
            return
        n = len(self._ctq_names)
        half = self._cell_w / 2.0
        half_y = half * self.FLATTEN
        centers = self._col_centers
        mx, my = event.position().x(), event.position().y()

        for i in range(n):
            for j in range(i + 1, n):
                cx = (centers[i] + centers[j]) / 2.0
                cy = self.height() - (j - i) * half_y
                if abs(mx - cx) / half + abs(my - cy) / half_y < 1:
                    self.correlation_clicked.emit(i, j)
                    return


# ══════════════════════════════════════════════════════════════════
#  HOQMatrixView — the complete integrated House of Quality
# ══════════════════════════════════════════════════════════════════
class HOQMatrixView(QWidget):
    data_changed = Signal()

    @property
    def RIGHT_COLS(self):
        """Right-wall column headers (translated at access time, not import time)."""
        return [t("hoq.col_ui"), t("hoq.col_ti"), t("hoq.col_ri"),
                t("hoq.col_si"), t("hoq.col_wai"), t("hoq.col_wi")]

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.project_id = None
        self.phase = 1
        self.symbol_mode = False  # default to numeric mode (9/3/1)
        self._vocs = []
        self._ctqs = []
        self._importance = {}
        self._setup_ui()

    # ── UI setup ─────────────────────────────────────────────────
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 8)
        layout.setSpacing(4)

        # Top toolbar
        toolbar = QHBoxLayout()
        lbl = QLabel(t("hoq.title"))
        lbl.setObjectName("title")
        toolbar.addWidget(lbl)
        toolbar.addStretch()

        # Legend
        for clr, txt in [(CLR_STRONG, t("hoq.strong")), (CLR_MEDIUM, t("hoq.medium")), (CLR_WEAK, t("hoq.weak"))]:
            dot = QLabel(f"  ■ {txt}")
            dot.setStyleSheet(f"color: {clr.name()}; font-weight: bold; font-size: 12px;")
            toolbar.addWidget(dot)

        toolbar.addWidget(QLabel("   "))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([t("hoq.symbol_mode"), t("hoq.number_mode")])
        self.mode_combo.setCurrentIndex(1)  # default to numeric mode
        self.mode_combo.currentIndexChanged.connect(self._toggle_mode)
        toolbar.addWidget(self.mode_combo)

        btn_recalc = QPushButton(t("hoq.recalc"))
        btn_recalc.setObjectName("secondary")
        btn_recalc.clicked.connect(self._recalculate)
        toolbar.addWidget(btn_recalc)
        layout.addLayout(toolbar)

        hint = QLabel(t("hoq.hint"))
        hint.setStyleSheet("color: #7F8C8D; font-size: 11px;")
        layout.addWidget(hint)

        # ── Roof (triangle) ──
        self.roof_widget = RoofWidget()
        self.roof_widget.correlation_clicked.connect(self._on_roof_clicked)

        # ── Main table ──
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.cellClicked.connect(self._on_cell_clicked)
        self.table.cellChanged.connect(self._on_cell_changed)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget { gridline-color: #BDBDBD; font-size: 12px; }
            QTableWidget::item { padding: 0px 2px; }
            QTableWidget::item:selected { color: #E74C3C; }
            QHeaderView::section {
                background-color: #FFF9C4; color: #333;
                font-weight: bold; font-size: 10px;
                border: 1px solid #BDBDBD; padding: 2px;
            }
            QLineEdit { background: white; color: #333; font-size: 13px;
                        border: 2px solid #1565C0; padding: 1px 2px; }
        """)

        # Scroll area wrapping roof + table
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)
        scroll_layout.addWidget(self.roof_widget)
        scroll_layout.addWidget(self.table)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Sync horizontal scroll between roof and table
        self.table.horizontalScrollBar().valueChanged.connect(self._sync_roof_scroll)

    def _sync_roof_scroll(self, value):
        # Recalculate roof offset based on table scroll position
        self._update_roof()

    # ── Data binding ─────────────────────────────────────────────
    def set_project(self, project_id, phase=1):
        self.project_id = project_id
        self.phase = phase
        self.refresh()

    def refresh(self):
        if not self.project_id:
            return
        self._vocs = [dict(v) for v in self.db.get_vocs(self.project_id, self.phase)]
        self._ctqs = [dict(c) for c in self.db.get_ctqs(self.project_id, self.phase)]
        self._build_table()
        self._update_roof()
        self._recalculate()

    # ── Build the integrated table ───────────────────────────────
    def _build_table(self):
        self.table.blockSignals(True)
        self.table.clearContents()  # Defensive: clear all cells before rebuild
        # clearContents() does NOT reset merged cell spans (setSpan). Since floor/
        # basement row & column positions are derived from nv/nc/n_comps, any span
        # left over from a previous render becomes stale (wrong position) as soon as
        # those counts change — corrupting the grid (merged/vanished cells). Reset
        # spans on every full rebuild before re-applying fresh ones.
        self.table.clearSpans()
        vocs = self._vocs
        ctqs = self._ctqs
        nv, nc = len(vocs), len(ctqs)

        comps = list(self.db.get_competitors(self.project_id))
        n_right = len(self.RIGHT_COLS)
        n_comp_cols = len(comps)  # one column per competitor for VOC satisfaction

        # Column layout: [Name][Ii] [CTQ1..n] [Ui Ti Ri Si Wai Wi] [Comp1..CompN]
        has_comps = len(comps) > 0
        total_cols = 2 + nc + n_right + n_comp_cols
        # Row layout: nv VOC rows + 2 floor rows (Tai/Ti + M) + ncomps basement rows
        n_bottom = 2 + len(comps)
        total_rows = nv + n_bottom
        self.table.setRowCount(total_rows)
        self.table.setColumnCount(total_cols)

        # ── Headers ──
        headers = [t("hoq.customer_req"), t("hoq.weight_ii")]
        dir_arrow = lambda c: DIRECTION_SYMBOLS.get(c.get('direction', ''), '')
        for c in ctqs:
            arrow = dir_arrow(c)
            unit = f"[{c['unit']}]" if c['unit'] else ""
            headers.append(f"{c['name']}\n{arrow}{unit}")
        headers += self.RIGHT_COLS
        for comp in comps:
            tag = "★" if comp['is_self'] else ""
            headers.append(f"{tag}{comp['name']}")
        self.table.setHorizontalHeaderLabels(headers)

        # Formatting
        self.table.horizontalHeader().setDefaultSectionSize(46)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.setColumnWidth(0, 110)
        self.table.setColumnWidth(1, 42)
        for i in range(n_right):
            self.table.setColumnWidth(2 + nc + i, 52)
        for i in range(n_comp_cols):
            self.table.setColumnWidth(2 + nc + n_right + i, 58)
        self.table.verticalHeader().setDefaultSectionSize(32)

        # ── Get relationship data ──
        rels = self.db.get_relationships(self.project_id, self.phase)
        rel_map = {(r['voc_id'], r['ctq_id']): r['strength'] for r in rels}

        # ── Fill VOC rows (Left Wall + Room + Right Wall) ──
        for i, v in enumerate(vocs):
            # Col 0: VOC name (Left Wall)
            name_item = QTableWidgetItem(v['name'])
            name_item.setFont(QFont("Microsoft YaHei", 9))
            name_item.setBackground(QColor("#FFF9C4"))
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 0, name_item)

            # Col 1: Importance Ii (EDITABLE)
            ii = v.get('importance', 3) or 3
            ii_item = QTableWidgetItem(f"{ii:.2f}")
            ii_item.setTextAlignment(Qt.AlignCenter)
            ii_item.setBackground(QColor('#E8F5E9'))
            ii_item.setFont(QFont("Microsoft YaHei", 9, QFont.Bold))
            ii_item.setData(Qt.UserRole, ("ii", v['id']))
            self.table.setItem(i, 1, ii_item)

            # Cols 2..2+nc-1: Relationship cells (Room)
            for j, c in enumerate(ctqs):
                strength = rel_map.get((v['id'], c['id']), 0) or 0
                s_int = int(strength)
                if self.symbol_mode:
                    text = HOQEngine.value_to_symbol(s_int)
                else:
                    text = str(s_int) if s_int else ""
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                item.setData(Qt.UserRole, ("rel", v['id'], c['id']))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                # Color-fill block
                bg = STRENGTH_COLORS.get(s_int, CLR_EMPTY)
                if s_int > 0:
                    item.setBackground(bg)
                    item.setForeground(QColor(Qt.white) if s_int == 9 else QColor(Qt.white))
                    item.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
                self.table.setItem(i, 2 + j, item)

            # Right wall columns: Ui(只读), Ti(可编辑), Ri(自动), Si(可编辑), Wai(自动), Wi(自动)
            # Ui is the VOC's own current_level — the single synced source shared
            # with the VOC module and the CBA self-competitor score (see database.py
            # sync_self_voc_score).
            ui = v.get('current_level', 0) or 0
            ti = v.get('planned_level', 0) or 0
            ri = ti / ui if ui > 0 else 0
            si = v.get('sales_point', 1.0) or 1.0
            wai = ri * si * ii

            col_base = 2 + nc
            # Ui (EDITABLE — synced with VOC module & CBA self-competitor score)
            ui_item = QTableWidgetItem(f"{ui:.1f}" if ui else "")
            ui_item.setTextAlignment(Qt.AlignCenter)
            ui_item.setData(Qt.UserRole, ("ui", v['id']))
            ui_item.setBackground(QColor('#E8F5E9'))
            self.table.setItem(i, col_base, ui_item)
            # Ti (EDITABLE)
            ti_item = QTableWidgetItem(f"{ti:.1f}" if ti else "")
            ti_item.setTextAlignment(Qt.AlignCenter)
            ti_item.setData(Qt.UserRole, ("ti", v['id']))
            ti_item.setBackground(QColor('#E8F5E9'))
            self.table.setItem(i, col_base + 1, ti_item)
            # Ri (auto)
            self.table.setItem(i, col_base + 2, self._readonly_item(f"{ri:.2f}" if ri else ""))
            # Si (EDITABLE — sales point)
            si_item = QTableWidgetItem(f"{si:.1f}")
            si_item.setTextAlignment(Qt.AlignCenter)
            si_item.setData(Qt.UserRole, ("si", v['id']))
            si_item.setBackground(QColor('#E8F5E9'))
            ti_item.setBackground(QColor('#E8F5E9'))
            self.table.setItem(i, col_base + 3, si_item)
            # Wai (auto — NOT bold)
            wai_item = self._readonly_item(f"{wai:.2f}" if wai else "")
            self.table.setItem(i, col_base + 4, wai_item)
            # Wi placeholder
            self.table.setItem(i, col_base + 5, self._readonly_item(""))

        # Fill Wi (normalized)
        total_wai = 0
        col_wai = 2 + nc + 4
        col_wi = 2 + nc + 5
        for i in range(nv):
            item = self.table.item(i, col_wai)
            if item and item.text():
                try: total_wai += float(item.text())
                except: pass
        for i in range(nv):
            item = self.table.item(i, col_wai)
            wai_val = 0
            if item and item.text():
                try: wai_val = float(item.text())
                except: pass
            wi = wai_val / total_wai if total_wai > 0 else 0
            wi_item = self._readonly_item(f"{wi:.3f}")
            self.table.setItem(i, col_wi, wi_item)

        # ── Right wall: Competitor VOC satisfaction columns ──
        comp_col_start = 2 + nc + n_right
        for ci_idx, comp in enumerate(comps):
            col = comp_col_start + ci_idx
            scores_map = {s['voc_id']: s['score'] for s in self.db.get_competitor_voc_scores(comp['id'])}
            for i, v in enumerate(vocs):
                score = scores_map.get(v['id'], 0)
                item = self._readonly_item(f"{score:.1f}" if score else "", bg="#E3F2FD")
                self.table.setItem(i, col, item)

        # ── Bottom rows (Floor / 地板 + Basement / 地下室) ──
        self._fill_bottom_rows(nv, nc, n_right, comps, n_comp_cols)
        self.table.blockSignals(False)

    def _fill_bottom_rows(self, nv, nc, n_right, comps, n_comp_cols=0):
        """Fill floor (Tai/Ti + M), basement (competitors + T)."""
        vocs = self._vocs
        ctqs = self._ctqs
        CLR_FLOOR = "#FFF9C4"
        CLR_COMP = "#E3F2FD"
        CLR_INDEX = "#BBDEFB"

        rels = [dict(r) for r in self.db.get_relationships(self.project_id, self.phase)]
        self._importance = HOQEngine.compute_importance(vocs, ctqs, rels)

        row_tai = nv
        row_ti = nv + 1
        has_comps = len(comps) > 0
        n_comps = len(comps)
        total_cols = self.table.columnCount()
        comp_col_start = 2 + nc + n_right

        # ── Tai row (NOT bold numbers) ──
        self.table.setItem(row_tai, 0, self._readonly_item(t("hoq.abs_weight"), bg=CLR_FLOOR))
        self.table.item(row_tai, 0).setFont(QFont("Microsoft YaHei", 9, QFont.Bold))
        self.table.setItem(row_tai, 1, self._readonly_item("Σrij·Ii", bg=CLR_FLOOR))

        # ── Ti row (BOLD numbers) ──
        self.table.setItem(row_ti, 0, self._readonly_item(t("hoq.rel_weight_row"), bg=CLR_FLOOR))
        self.table.item(row_ti, 0).setFont(QFont("Microsoft YaHei", 9, QFont.Bold))
        self.table.setItem(row_ti, 1, self._readonly_item("Tai/ΣTai", bg=CLR_FLOOR))

        for j, c in enumerate(ctqs):
            imp = self._importance.get(c['id'], {})
            abs_val = imp.get('absolute_importance', 0)
            rel_val = imp.get('relative_importance', 0)
            self.table.setItem(row_tai, 2 + j, self._readonly_item(f"{abs_val:.1f}", bg=CLR_FLOOR))
            ti_item = self._readonly_item(f"{rel_val/100:.3f}" if rel_val else "0", bg=CLR_FLOOR)
            self.table.setItem(row_ti, 2 + j, ti_item)

        # Fill right-wall area of floor
        for row in [row_tai, row_ti]:
            for col in range(2 + nc, comp_col_start):
                if not self.table.item(row, col):
                    self.table.setItem(row, col, self._readonly_item("", bg=CLR_FLOOR))

        # ── M (customer satisfaction index) values in Tai row + label in Ti row ──
        if has_comps:
            # Smax = max of the competitor VOC satisfaction score scale (always
            # 1-5, see competition_view.py score clamp), NOT the project's
            # importance_scale (which rates VOC importance Ii, a different scale).
            max_scale = 5

            for ci, comp in enumerate(comps):
                col = comp_col_start + ci
                scores = {s['voc_id']: s['score'] for s in self.db.get_competitor_voc_scores(comp['id'])}
                w_sum, t_ii = 0, 0
                for v in vocs:
                    sc = scores.get(v['id'], 0)
                    ii = v.get('importance', 0) or 0
                    if sc and ii:
                        w_sum += sc * ii
                        t_ii += ii
                m = w_sum / (t_ii * max_scale) if (t_ii * max_scale) > 0 else 0
                m_item = self._readonly_item(f"{m:.3f}", bg=CLR_INDEX)
                m_item.setFont(QFont("Microsoft YaHei", 9, QFont.Bold))
                self.table.setItem(row_tai, col, m_item)

            # "M" merged label in Ti row across all competitor columns
            if n_comps > 1:
                self.table.setSpan(row_ti, comp_col_start, 1, n_comps)
            m_lbl = self._readonly_item("M", bg=CLR_INDEX)
            m_lbl.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
            self.table.setItem(row_ti, comp_col_start, m_lbl)

        # ── Basement: Competitor rows + T (technical competitiveness index) ──
        comp_ctq_scores = {}
        for comp in comps:
            for s in self.db.get_competitor_ctq_scores(comp['id']):
                comp_ctq_scores[(comp['id'], s['ctq_id'])] = s['value']

        col_ui = 2 + nc      # Ui column
        col_ti_rw = 2 + nc + 1   # Ti column (right wall)
        basement_start = nv + 2

        for ci, comp in enumerate(comps):
            row = basement_start + ci
            name_item = self._readonly_item(comp['name'], bg=CLR_COMP)
            name_item.setFont(QFont("Microsoft YaHei", 9, QFont.Bold))
            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, self._readonly_item("", bg=CLR_COMP))

            # CTQ benchmark values
            for j, c in enumerate(ctqs):
                val = comp_ctq_scores.get((comp['id'], c['id']), "")
                self.table.setItem(row, 2 + j, self._readonly_item(str(val), bg=CLR_COMP))

            # Compute T (TCI)
            vals = []
            for c in ctqs:
                raw = comp_ctq_scores.get((comp['id'], c['id']), "")
                try: vals.append(float(raw))
                except: vals.append(0)

            t_sum, tai_sum = 0, 0
            for j, c in enumerate(ctqs):
                tai = self._importance.get(c['id'], {}).get('absolute_importance', 0)
                all_vals = []
                for comp2 in comps:
                    raw2 = comp_ctq_scores.get((comp2['id'], c['id']), "")
                    try: all_vals.append(float(raw2))
                    except: pass
                max_val = max(all_vals) if all_vals else 1
                min_val = min(v2 for v2 in all_vals if v2 > 0) if any(v2 > 0 for v2 in all_vals) else 1
                direction = c.get('direction', 'higher_better')
                if max_val > 0 and vals[j] > 0:
                    norm = (min_val / vals[j]) if direction == 'lower_better' else (vals[j] / max_val)
                    t_sum += tai * norm
                    tai_sum += tai
            t_val = t_sum / tai_sum if tai_sum > 0 else 0

            # T value → Ui column of this basement row
            t_item = self._readonly_item(f"{t_val:.3f}", bg=CLR_INDEX)
            t_item.setFont(QFont("Microsoft YaHei", 9, QFont.Bold))
            self.table.setItem(row, col_ui, t_item)

            # Fill remaining right-wall + competitor cols
            for col in range(col_ti_rw, total_cols):
                if not self.table.item(row, col):
                    self.table.setItem(row, col, self._readonly_item("", bg=CLR_COMP))

        # "T" merged label in Ti column, spanning all competitor rows vertically —
        # same highlight color as the T value cells to its left, for consistency
        if has_comps and n_comps > 0:
            if n_comps > 1:
                self.table.setSpan(basement_start, col_ti_rw, n_comps, 1)
            t_lbl = self._readonly_item("T", bg=CLR_INDEX)
            t_lbl.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
            self.table.setItem(basement_start, col_ti_rw, t_lbl)

    def _readonly_item(self, text, bg=None):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        if bg:
            item.setBackground(QColor(bg))
        return item

    # ── Roof update ──────────────────────────────────────────────
    def _update_roof(self):
        ctqs = self._ctqs
        if not ctqs:
            self.roof_widget.set_data([], {}, [])
            return

        corrs = self.db.get_roof_correlations(self.project_id, self.phase)
        id_to_idx = {c['id']: i for i, c in enumerate(ctqs)}
        corr_data = {}
        for cr in corrs:
            i = id_to_idx.get(cr['ctq_id_1'])
            j = id_to_idx.get(cr['ctq_id_2'])
            if i is not None and j is not None:
                a, b = min(i, j), max(i, j)
                corr_data[(a, b)] = cr['correlation']

        # Column centers come straight from the table's actual on-screen column
        # positions (already scroll-adjusted) rather than assuming every CTQ
        # column is exactly defaultSectionSize wide — a manually-resized column
        # would otherwise silently drift the roof out of alignment by the time
        # you reach the later columns.
        nc = len(ctqs)
        col_centers = [self.table.columnViewportPosition(2 + i) + self.table.columnWidth(2 + i) / 2.0
                       for i in range(nc)]
        cw = self.table.horizontalHeader().defaultSectionSize()

        names = [c['name'] for c in ctqs]
        self.roof_widget.set_data(names, corr_data, col_centers, cell_w=cw)

    # ── Cell click handler (Room) ────────────────────────────────
    def _on_cell_clicked(self, row, col):
        nv = len(self._vocs)
        nc = len(self._ctqs)
        # Only handle relationship cells (Room area)
        if row >= nv or col < 2 or col >= 2 + nc:
            return
        item = self.table.item(row, col)
        if not item:
            return
        data = item.data(Qt.UserRole)
        if not data or data[0] != "rel":
            return
        _, voc_id, ctq_id = data

        rel = self.db.get_relationship(self.project_id, voc_id, ctq_id, self.phase)
        current = int(rel['strength']) if rel else 0
        cycle = [0, 1, 3, 9]
        idx = cycle.index(current) if current in cycle else 0
        new_val = cycle[(idx + 1) % len(cycle)]

        self.db.set_relationship(self.project_id, voc_id, ctq_id, new_val,
                                  phase=self.phase,
                                  symbol=HOQEngine.value_to_symbol(new_val))
        self._build_table()
        self._recalculate()
        self.data_changed.emit()

    # ── Cell changed handler (Ti edits) ──────────────────────────
    def _on_cell_changed(self, row, col):
        """Handle edits to Ii(importance), Ti(planned level), Si(sales point)."""
        nv = len(self._vocs)
        nc = len(self._ctqs)
        if row >= nv:
            return
        item = self.table.item(row, col)
        if not item:
            return
        data = item.data(Qt.UserRole)
        if not data or not isinstance(data, tuple) or len(data) < 2:
            return

        tag, voc_id = data[0], data[1]
        try:
            val = float(item.text()) if item.text().strip() else 0
        except ValueError:
            return

        # Save to database
        if tag == "ii":
            self.db.update_voc(voc_id, importance=val)
            self._vocs[row]['importance'] = val
        elif tag == "ui":
            # Goes through the sync helper so the VOC module's Ui field and
            # CBA's self-competitor score stay identical to what's entered here.
            self.db.sync_self_voc_score(self.project_id, voc_id, val)
            self._vocs[row]['current_level'] = val
        elif tag == "ti":
            self.db.update_voc(voc_id, planned_level=val)
            self._vocs[row]['planned_level'] = val
        elif tag == "si":
            self.db.update_voc(voc_id, sales_point=val)
            self._vocs[row]['sales_point'] = val
        else:
            return

        # Update computed cells in-place (don't rebuild entire table)
        self.table.blockSignals(True)
        v = self._vocs[row]
        ii = v.get('importance', 0) or 0
        ti = v.get('planned_level', 0) or 0
        si = v.get('sales_point', 1.0) or 1.0

        # Find Ui from current cell value
        col_base = 2 + nc
        ui_item = self.table.item(row, col_base)
        ui = 0
        if ui_item and ui_item.text():
            try: ui = float(ui_item.text())
            except: pass

        ri = ti / ui if ui > 0 else 0
        wai = ri * si * ii

        # Update Ri, Wai cells
        ri_item = self.table.item(row, col_base + 2)
        if ri_item:
            ri_item.setText(f"{ri:.2f}" if ri else "")
        si_cell = self.table.item(row, col_base + 3)
        if si_cell and tag == "si":
            pass  # Already updated by the user
        wai_cell = self.table.item(row, col_base + 4)
        if wai_cell:
            wai_cell.setText(f"{wai:.2f}" if wai else "")

        # Recalculate Wi for ALL rows
        total_wai = 0
        col_wai = col_base + 4
        col_wi = col_base + 5
        for i in range(nv):
            wi_item = self.table.item(i, col_wai)
            if wi_item and wi_item.text():
                try: total_wai += float(wi_item.text())
                except: pass
        for i in range(nv):
            wi_item = self.table.item(i, col_wai)
            w_val = 0
            if wi_item and wi_item.text():
                try: w_val = float(wi_item.text())
                except: pass
            wi = w_val / total_wai if total_wai > 0 else 0
            target = self.table.item(i, col_wi)
            if target:
                target.setText(f"{wi:.3f}")

        self.table.blockSignals(False)

        # Also refresh floor (Tai/Ti/M/C) if Ii changed — Ii feeds directly into
        # Tai and (via VOC weighting) M, so those displayed cells must update too.
        # _recalculate() alone only updates self._importance, not the visible cells.
        if tag == "ii":
            self._build_table()

        self.data_changed.emit()

    # ── Roof click handler ───────────────────────────────────────
    def _on_roof_clicked(self, i, j):
        if i >= len(self._ctqs) or j >= len(self._ctqs):
            return
        id1 = self._ctqs[i]['id']
        id2 = self._ctqs[j]['id']

        corrs = self.db.get_roof_correlations(self.project_id, self.phase)
        id_min, id_max = min(id1, id2), max(id1, id2)
        current = ""
        for cr in corrs:
            if cr['ctq_id_1'] == id_min and cr['ctq_id_2'] == id_max:
                current = cr['correlation']
                break

        cycle = ['', '+', '++', '-', '--']
        idx = cycle.index(current) if current in cycle else 0
        new_val = cycle[(idx + 1) % len(cycle)]

        self.db.set_roof_correlation(self.project_id, id1, id2, new_val, self.phase)
        self._update_roof()
        self.data_changed.emit()

    # ── Recalculate importance ───────────────────────────────────
    def _recalculate(self):
        if not self._vocs or not self._ctqs:
            return
        rels = [dict(r) for r in self.db.get_relationships(self.project_id, self.phase)]
        self._importance = HOQEngine.compute_importance(self._vocs, self._ctqs, rels)

    def _toggle_mode(self, index):
        self.symbol_mode = (index == 0)
        self._build_table()

    def get_importance_data(self):
        return self._importance
