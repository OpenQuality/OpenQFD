"""
Competition Benchmarking Analysis View
Supports competitor management, VOC/CTQ scoring, radar charts, bar charts.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QDoubleSpinBox,
    QGroupBox, QFormLayout, QMessageBox, QHeaderView, QAbstractItemView,
    QSplitter, QTabWidget, QCheckBox, QColorDialog, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

import numpy as np

from views.styles import COLORS
from utils.i18n import t


class CompetitionView(QWidget):
    data_changed = Signal()

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.project_id = None
        self.phase = 1
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header
        header = QHBoxLayout()
        lbl = QLabel(t("comp.title"))
        lbl.setObjectName("title")
        header.addWidget(lbl)
        header.addStretch()

        btn_add = QPushButton(t("comp.add"))
        btn_add.clicked.connect(self._add_competitor)
        header.addWidget(btn_add)

        btn_del = QPushButton(t("comp.delete"))
        btn_del.setObjectName("danger")
        btn_del.clicked.connect(self._delete_competitor)
        header.addWidget(btn_del)
        layout.addLayout(header)

        self.tabs = QTabWidget()

        # Tab 1: Competitor list
        comp_tab = QWidget()
        comp_layout = QVBoxLayout(comp_tab)
        self.comp_table = QTableWidget()
        self.comp_table.setColumnCount(3)
        self.comp_table.setHorizontalHeaderLabels([t("comp.col_name"), t("comp.col_is_self"), t("comp.col_color")])
        self.comp_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.comp_table.setAlternatingRowColors(True)
        self.comp_table.verticalHeader().setDefaultSectionSize(34)
        comp_layout.addWidget(self.comp_table)
        self.tabs.addTab(comp_tab, t("comp.tab_manage"))

        # Tab 2: VOC scoring
        voc_tab = QWidget()
        voc_layout = QVBoxLayout(voc_tab)
        hint = QLabel(t("comp.voc_hint"))
        hint.setObjectName("subtitle")
        voc_layout.addWidget(hint)
        self.voc_score_table = QTableWidget()
        self.voc_score_table.setAlternatingRowColors(True)
        self.voc_score_table.verticalHeader().setDefaultSectionSize(34)
        self.voc_score_table.setStyleSheet("QTableWidget::item { padding: 0px 3px; font-size: 13px; }")
        self.voc_score_table.cellChanged.connect(self._on_voc_score_changed)
        voc_layout.addWidget(self.voc_score_table)
        self.tabs.addTab(voc_tab, t("comp.tab_voc"))

        # Tab 3: CTQ scoring
        ctq_tab = QWidget()
        ctq_layout = QVBoxLayout(ctq_tab)
        hint2 = QLabel(t("comp.ctq_hint"))
        hint2.setObjectName("subtitle")
        ctq_layout.addWidget(hint2)
        self.ctq_score_table = QTableWidget()
        self.ctq_score_table.setAlternatingRowColors(True)
        self.ctq_score_table.verticalHeader().setDefaultSectionSize(34)
        self.ctq_score_table.setStyleSheet("QTableWidget::item { padding: 0px 3px; font-size: 13px; }")
        self.ctq_score_table.cellChanged.connect(self._on_ctq_score_changed)
        ctq_layout.addWidget(self.ctq_score_table)
        self.tabs.addTab(ctq_tab, t("comp.tab_ctq"))

        # Tab 4: Charts
        chart_tab = QWidget()
        chart_layout = QVBoxLayout(chart_tab)

        chart_toolbar = QHBoxLayout()
        btn_radar = QPushButton(t("comp.radar"))
        btn_radar.clicked.connect(self._generate_radar)
        chart_toolbar.addWidget(btn_radar)

        btn_bar = QPushButton(t("comp.bar"))
        btn_bar.clicked.connect(self._generate_bar_chart)
        chart_toolbar.addWidget(btn_bar)
        chart_toolbar.addStretch()
        chart_layout.addLayout(chart_toolbar)

        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
        from matplotlib.figure import Figure
        from utils.fonts import setup_matplotlib_fonts
        setup_matplotlib_fonts()

        self.fig = Figure(figsize=(8, 5), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.fig)
        chart_layout.addWidget(self.canvas)
        self.tabs.addTab(chart_tab, t("comp.tab_chart"))

        layout.addWidget(self.tabs)

    def set_project(self, project_id, phase=1):
        self.project_id = project_id
        self.phase = phase
        self.refresh()

    def refresh(self):
        if not self.project_id:
            return
        self._refresh_comp_table()
        self._refresh_voc_scores()
        self._refresh_ctq_scores()
        # Clear the stale radar/bar chart from a previously loaded project —
        # it only gets regenerated when the user clicks "生成雷达图"/"生成柱状对比图" again.
        self.fig.clear()
        self.canvas.draw()

    def _refresh_comp_table(self):
        comps = self.db.get_competitors(self.project_id)
        self.comp_table.setRowCount(len(comps))
        for i, c in enumerate(comps):
            name_item = QTableWidgetItem(c['name'])
            name_item.setData(Qt.UserRole, c['id'])
            self.comp_table.setItem(i, 0, name_item)

            self_item = QTableWidgetItem(t("comp.is_self_mark") if c['is_self'] else "")
            self_item.setTextAlignment(Qt.AlignCenter)
            if c['is_self']:
                self_item.setForeground(QColor(COLORS['success']))
            self.comp_table.setItem(i, 1, self_item)

            color_item = QTableWidgetItem("  ")
            color_item.setBackground(QColor(c['color']))
            self.comp_table.setItem(i, 2, color_item)

    def _refresh_voc_scores(self):
        self.voc_score_table.blockSignals(True)
        comps = self.db.get_competitors(self.project_id)
        vocs = self.db.get_vocs(self.project_id, self.phase)

        self.voc_score_table.setRowCount(len(vocs))
        self.voc_score_table.setColumnCount(len(comps))
        self.voc_score_table.setHorizontalHeaderLabels([c['name'] for c in comps])
        self.voc_score_table.setVerticalHeaderLabels([v['name'] for v in vocs])

        for j, comp in enumerate(comps):
            scores = {s['voc_id']: s['score'] for s in self.db.get_competitor_voc_scores(comp['id'])}
            for i, voc in enumerate(vocs):
                score = scores.get(voc['id'], 0)
                item = QTableWidgetItem(f"{score:.1f}" if score else "")
                item.setTextAlignment(Qt.AlignCenter)
                item.setData(Qt.UserRole, (comp['id'], voc['id']))
                self.voc_score_table.setItem(i, j, item)

        self.voc_score_table.blockSignals(False)

    def _refresh_ctq_scores(self):
        self.ctq_score_table.blockSignals(True)
        comps = self.db.get_competitors(self.project_id)
        ctqs = self.db.get_ctqs(self.project_id, self.phase)

        self.ctq_score_table.setRowCount(len(ctqs))
        self.ctq_score_table.setColumnCount(len(comps))
        self.ctq_score_table.setHorizontalHeaderLabels([c['name'] for c in comps])
        self.ctq_score_table.setVerticalHeaderLabels([f"{c['name']} [{c['unit']}]" for c in ctqs])

        for j, comp in enumerate(comps):
            scores = {s['ctq_id']: s['value'] for s in self.db.get_competitor_ctq_scores(comp['id'])}
            for i, ctq in enumerate(ctqs):
                val = scores.get(ctq['id'], '')
                item = QTableWidgetItem(str(val) if val else "")
                item.setTextAlignment(Qt.AlignCenter)
                item.setData(Qt.UserRole, (comp['id'], ctq['id']))
                self.ctq_score_table.setItem(i, j, item)

        self.ctq_score_table.blockSignals(False)

    def _add_competitor(self):
        if not self.project_id:
            return
        comps = self.db.get_competitors(self.project_id)
        if len(comps) >= 5:
            QMessageBox.warning(self, t("comp.limit_title"), t("comp.max_competitors"))
            return
        colors = ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6']
        color = colors[len(comps) % len(colors)]
        is_self = len(comps) == 0  # First one defaults to self
        name = t("comp.our_product") if is_self else t("comp.competitor_n", n=len(comps))
        self.db.add_competitor(self.project_id, name, is_self=is_self, color=color)
        self.refresh()
        self.data_changed.emit()

    def _delete_competitor(self):
        row = self.comp_table.currentRow()
        if row < 0:
            return
        item = self.comp_table.item(row, 0)
        comp_id = item.data(Qt.UserRole)
        reply = QMessageBox.question(self, t("common.confirm"), t("comp.confirm_delete", name=item.text()))
        if reply == QMessageBox.Yes:
            self.db.delete_competitor(comp_id)
            self.refresh()
            self.data_changed.emit()

    def _on_voc_score_changed(self, row, col):
        item = self.voc_score_table.item(row, col)
        if not item:
            return
        data = item.data(Qt.UserRole)
        if not data:
            return
        comp_id, voc_id = data
        try:
            score = float(item.text()) if item.text() else 0
            score = max(0, min(5, score))
            # If this is "our own product" (self), route through the sync helper
            # so the VOC module's Ui field and HOQ's Ui column update too.
            comp = self.db.conn.execute(
                "SELECT is_self FROM competitor WHERE id=?", (comp_id,)).fetchone()
            if comp and comp['is_self']:
                self.db.sync_self_voc_score(self.project_id, voc_id, score)
            else:
                self.db.set_competitor_voc_score(comp_id, voc_id, score)
        except ValueError:
            pass

    def _on_ctq_score_changed(self, row, col):
        item = self.ctq_score_table.item(row, col)
        if not item:
            return
        data = item.data(Qt.UserRole)
        if not data:
            return
        comp_id, ctq_id = data
        comp = self.db.conn.execute(
            "SELECT is_self FROM competitor WHERE id=?", (comp_id,)).fetchone()
        if comp and comp['is_self']:
            self.db.sync_self_ctq_score(self.project_id, ctq_id, item.text())
        else:
            self.db.set_competitor_ctq_score(comp_id, ctq_id, item.text())

    def _generate_radar(self):
        comps = self.db.get_competitors(self.project_id)
        vocs = self.db.get_vocs(self.project_id, self.phase)
        if not comps or not vocs:
            QMessageBox.information(self, t("common.hint"), t("comp.need_data_hint"))
            return

        self.fig.clear()
        ax = self.fig.add_subplot(111, polar=True)

        labels = [v['name'] for v in vocs]
        n = len(labels)
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
        angles += angles[:1]

        for comp in comps:
            scores_map = {s['voc_id']: s['score'] for s in self.db.get_competitor_voc_scores(comp['id'])}
            values = [scores_map.get(v['id'], 0) for v in vocs]
            values += values[:1]
            ax.plot(angles, values, 'o-', linewidth=2, label=comp['name'], color=comp['color'])
            ax.fill(angles, values, alpha=0.1, color=comp['color'])

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_ylim(0, 5.5)
        ax.set_title(t("comp.radar_title"), fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        self.fig.tight_layout()
        self.canvas.draw()

    def _generate_bar_chart(self):
        comps = self.db.get_competitors(self.project_id)
        vocs = self.db.get_vocs(self.project_id, self.phase)
        if not comps or not vocs:
            return

        self.fig.clear()
        ax = self.fig.add_subplot(111)

        x = np.arange(len(vocs))
        width = 0.8 / max(len(comps), 1)

        for idx, comp in enumerate(comps):
            scores_map = {s['voc_id']: s['score'] for s in self.db.get_competitor_voc_scores(comp['id'])}
            values = [scores_map.get(v['id'], 0) for v in vocs]
            ax.bar(x + idx * width, values, width, label=comp['name'], color=comp['color'], alpha=0.85)

        ax.set_xlabel(t("comp.bar_xlabel"))
        ax.set_ylabel(t("comp.bar_ylabel"))
        ax.set_title(t("comp.bar_title"), fontsize=14, fontweight='bold')
        ax.set_xticks(x + width * (len(comps) - 1) / 2)
        ax.set_xticklabels([v['name'] for v in vocs], rotation=45, ha='right', fontsize=9)
        ax.legend()
        ax.set_ylim(0, 5.5)
        ax.grid(axis='y', alpha=0.3)
        self.fig.tight_layout()
        self.canvas.draw()
