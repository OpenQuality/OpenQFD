"""
Multi-Phase QFD Deployment View (4 stages: ASI model)
Supports cascade flow between phases.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QMessageBox, QFrame, QSplitter, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QComboBox, QTextEdit, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from utils.fonts import setup_matplotlib_fonts
setup_matplotlib_fonts()

from engines.compute import HOQEngine
from views.styles import COLORS, PHASE_NAMES, PHASE_ROW_LABELS, PHASE_COL_LABELS
from utils.i18n import t


class PhaseView(QWidget):
    phase_changed = Signal(int)

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.project_id = None
        self._setup_ui()

    def _setup_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        outer_layout.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()
        lbl = QLabel(t("phase.title"))
        lbl.setObjectName("title")
        header.addWidget(lbl)
        header.addStretch()
        layout.addLayout(header)

        hint = QLabel(t("phase.hint"))
        hint.setObjectName("subtitle")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        # Phase cards
        phases_layout = QHBoxLayout()
        self.phase_cards = {}

        for phase_num in range(1, 5):
            card = self._create_phase_card(phase_num)
            phases_layout.addWidget(card)
            if phase_num < 4:
                arrow = QLabel("  ➜  ")
                arrow.setFont(QFont("Microsoft YaHei", 20))
                arrow.setStyleSheet("color: #1B5E8C;")
                phases_layout.addWidget(arrow)

        layout.addLayout(phases_layout)

        # Cascade controls
        cascade_group = QGroupBox(t("phase.cascade_group"))
        cascade_layout = QHBoxLayout(cascade_group)

        for phase_num in range(1, 4):
            btn = QPushButton(t("phase.cascade", a=phase_num, b=phase_num + 1))
            btn.setObjectName("accent")
            btn.clicked.connect(lambda _, p=phase_num: self._cascade_phase(p))
            cascade_layout.addWidget(btn)

        layout.addWidget(cascade_group)

        # Topology view
        topo_group = QGroupBox(t("phase.topology_group"))
        topo_layout = QVBoxLayout(topo_group)
        self.fig = Figure(figsize=(10, 3), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.setMinimumHeight(280)
        topo_layout.addWidget(self.canvas)
        layout.addWidget(topo_group)

        # Phase detail table
        detail_group = QGroupBox(t("phase.detail_group"))
        detail_layout = QVBoxLayout(detail_group)

        self.phase_combo = QComboBox()
        for p in PHASE_NAMES:
            self.phase_combo.addItem(t(f"phase.{p}"), p)
        self.phase_combo.currentIndexChanged.connect(self._on_phase_selected)
        detail_layout.addWidget(self.phase_combo)

        self.detail_table = QTableWidget()
        self.detail_table.verticalHeader().setDefaultSectionSize(32)
        self.detail_table.setAlternatingRowColors(True)
        self.detail_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.detail_table.setMinimumHeight(220)
        detail_layout.addWidget(self.detail_table)
        layout.addWidget(detail_group)

    def _create_phase_card(self, phase_num):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {COLORS['border']};
                border-radius: 10px;
                padding: 12px;
            }}
            QFrame:hover {{
                border-color: {COLORS['primary']};
                background-color: {COLORS['hover']};
            }}
        """)
        card_layout = QVBoxLayout(card)

        title = QLabel(t("phase.card_title", n=phase_num))
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['primary']};")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)

        name = QLabel(t(f"phase.short.{phase_num}"))
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet("color: #2C3E50; font-size: 13px;")
        card_layout.addWidget(name)

        row_label = QLabel(t("phase.row_label", v=t(f"phase.row.{phase_num}")))
        row_label.setStyleSheet("color: #7F8C8D; font-size: 11px;")
        card_layout.addWidget(row_label)

        col_label = QLabel(t("phase.col_label", v=t(f"phase.col.{phase_num}")))
        col_label.setStyleSheet("color: #7F8C8D; font-size: 11px;")
        card_layout.addWidget(col_label)

        # Counts
        self.phase_cards[phase_num] = {
            'card': card,
            'row_count': QLabel(t("phase.row_count", n=0)),
            'col_count': QLabel(t("phase.col_count", n=0)),
        }
        self.phase_cards[phase_num]['row_count'].setAlignment(Qt.AlignCenter)
        self.phase_cards[phase_num]['col_count'].setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.phase_cards[phase_num]['row_count'])
        card_layout.addWidget(self.phase_cards[phase_num]['col_count'])

        btn = QPushButton(t("phase.open_edit"))
        btn.setObjectName("secondary")
        btn.clicked.connect(lambda _, p=phase_num: self.phase_changed.emit(p))
        card_layout.addWidget(btn)

        return card

    def set_project(self, project_id):
        self.project_id = project_id
        self.refresh()

    def refresh(self):
        if not self.project_id:
            return

        for phase_num in range(1, 5):
            vocs = self.db.get_vocs(self.project_id, phase_num)
            ctqs = self.db.get_ctqs(self.project_id, phase_num)
            if phase_num in self.phase_cards:
                self.phase_cards[phase_num]['row_count'].setText(t("phase.row_count", n=len(vocs)))
                self.phase_cards[phase_num]['col_count'].setText(t("phase.col_count", n=len(ctqs)))

        self._draw_topology()
        self._on_phase_selected()

    def _cascade_phase(self, from_phase):
        """Cascade: Copy upstream CTQs as downstream VOCs."""
        ctqs = self.db.get_ctqs(self.project_id, from_phase)
        to_phase = from_phase + 1

        if not ctqs:
            QMessageBox.warning(self, t("common.hint"), t("phase.cascade_no_ctq", n=from_phase))
            return

        existing = self.db.get_vocs(self.project_id, to_phase)
        if existing:
            reply = QMessageBox.question(self, t("common.confirm"),
                t("phase.cascade_confirm_body", n=to_phase, count=len(existing)),
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                return
            if reply == QMessageBox.No:
                # Clear existing
                for v in existing:
                    self.db.delete_voc(v['id'])

        # Compute importance from upstream
        vocs_up = [dict(v) for v in self.db.get_vocs(self.project_id, from_phase)]
        rels_up = [dict(r) for r in self.db.get_relationships(self.project_id, from_phase)]
        importance = HOQEngine.compute_importance(vocs_up, [dict(c) for c in ctqs], rels_up)

        # Create VOCs in downstream phase
        for c in ctqs:
            imp = importance.get(c['id'], {})
            rel_imp = imp.get('relative_importance', 0)
            # Scale to 1-5
            scaled_imp = max(1.0, min(5.0, rel_imp / 20))

            self.db.add_voc(
                self.project_id,
                c['name'],
                phase=to_phase,
                importance=round(scaled_imp, 1),
                description=t("phase.cascade_desc", n=from_phase, name=c['name'], v=f"{rel_imp:.1f}"),
                source=t("phase.cascade_source", n=from_phase)
            )

        self.refresh()
        QMessageBox.information(self, t("phase.cascade_done_title"),
            t("phase.cascade_done_body", count=len(ctqs), a=from_phase, b=to_phase))

    def _draw_topology(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_xlim(-0.5, 8)
        ax.set_ylim(-0.5, 2)
        ax.axis('off')

        phase_positions = {1: 0.5, 2: 2.5, 3: 4.5, 4: 6.5}
        colors = ['#3498DB', '#2ECC71', '#E67E22', '#E74C3C']

        for i, (phase_num, x) in enumerate(phase_positions.items()):
            vocs = self.db.get_vocs(self.project_id, phase_num)
            ctqs = self.db.get_ctqs(self.project_id, phase_num)

            # Box
            rect = matplotlib.patches.FancyBboxPatch(
                (x - 0.4, 0.2), 1.3, 1.2,
                boxstyle="round,pad=0.1",
                facecolor=colors[i], alpha=0.15,
                edgecolor=colors[i], linewidth=2
            )
            ax.add_patch(rect)

            ax.text(x + 0.25, 1.2, t("phase.card_title", n=phase_num),
                   ha='center', fontsize=11, fontweight='bold', color=colors[i])
            ax.text(x + 0.25, 0.85, t(f"phase.short.{phase_num}"),
                   ha='center', fontsize=9, color='#2C3E50')
            ax.text(x + 0.25, 0.55, t("phase.rowcol_count", r=len(vocs), c=len(ctqs)),
                   ha='center', fontsize=9, color='#7F8C8D')

            # Arrow to next
            if phase_num < 4:
                ax.annotate('', xy=(x + 1.3, 0.8), xytext=(x + 0.9, 0.8),
                           arrowprops=dict(arrowstyle='->', color=COLORS['primary'],
                                          lw=2, connectionstyle='arc3'))

        ax.set_title(t("phase.topology_title"), fontsize=13, fontweight='bold', pad=10)
        try:
            self.fig.tight_layout()
        except Exception:
            self.fig.subplots_adjust(left=0.05, right=0.95, top=0.88, bottom=0.1)
        self.canvas.draw()

    def _on_phase_selected(self):
        phase = self.phase_combo.currentData()
        if not phase or not self.project_id:
            return

        vocs = self.db.get_vocs(self.project_id, phase)
        ctqs = self.db.get_ctqs(self.project_id, phase)

        # Show summary
        self.detail_table.setColumnCount(4)
        self.detail_table.setHorizontalHeaderLabels([
            t("phase.detail_row_header", v=t(f"phase.row.{phase}")), t("phase.importance"),
            t("phase.detail_col_header", v=t(f"phase.col.{phase}")), t("phase.difficulty")
        ])
        max_rows = max(len(vocs), len(ctqs))
        self.detail_table.setRowCount(max_rows)
        self.detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for i in range(max_rows):
            if i < len(vocs):
                self.detail_table.setItem(i, 0, QTableWidgetItem(vocs[i]['name']))
                self.detail_table.setItem(i, 1, QTableWidgetItem(f"{vocs[i]['importance']:.2f}"))
            if i < len(ctqs):
                self.detail_table.setItem(i, 2, QTableWidgetItem(ctqs[i]['name']))
                self.detail_table.setItem(i, 3, QTableWidgetItem(f"{ctqs[i]['difficulty']:.1f}"))
