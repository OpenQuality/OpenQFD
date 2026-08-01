"""
Advanced Analysis Views: AHP, Kano Classification, Pareto Chart
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QDoubleSpinBox,
    QGroupBox, QFormLayout, QMessageBox, QHeaderView, QAbstractItemView,
    QSplitter, QTabWidget, QFrame, QTextEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from utils.fonts import setup_matplotlib_fonts
setup_matplotlib_fonts()

from engines.compute import AHPEngine, KanoEngine, HOQEngine
from views.styles import COLORS, KANO_TYPES, KANO_TYPE_KEYS
from utils.i18n import t


class AHPView(QWidget):
    weights_computed = Signal(dict)  # {voc_id: weight}

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.project_id = None
        self.phase = 1
        self._vocs = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()
        lbl = QLabel(t("ahp.title"))
        lbl.setObjectName("title")
        header.addWidget(lbl)
        header.addStretch()

        btn_calc = QPushButton(t("ahp.compute"))
        btn_calc.clicked.connect(self._compute)
        header.addWidget(btn_calc)

        btn_apply = QPushButton(t("ahp.apply"))
        btn_apply.setObjectName("success")
        btn_apply.clicked.connect(self._apply_weights)
        header.addWidget(btn_apply)
        layout.addLayout(header)

        hint = QLabel(t("ahp.hint"))
        hint.setObjectName("subtitle")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        splitter = QSplitter(Qt.Vertical)

        # Comparison matrix
        self.matrix_table = QTableWidget()
        self.matrix_table.setAlternatingRowColors(False)
        self.matrix_table.verticalHeader().setDefaultSectionSize(36)
        self.matrix_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.matrix_table.setStyleSheet("QTableWidget::item { padding: 0px 3px; font-size: 13px; }")
        self.matrix_table.cellChanged.connect(self._on_cell_changed)
        splitter.addWidget(self.matrix_table)

        # Results
        bottom = QWidget()
        bottom_layout = QHBoxLayout(bottom)

        # Results table
        result_group = QGroupBox(t("ahp.result_group"))
        result_layout = QVBoxLayout(result_group)
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setHorizontalHeaderLabels([t("ahp.col_name"), t("ahp.col_weight"), t("ahp.col_normalized")])
        self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.result_table.verticalHeader().setDefaultSectionSize(32)
        self.result_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        result_layout.addWidget(self.result_table)
        bottom_layout.addWidget(result_group)

        # Consistency info
        info_group = QGroupBox(t("ahp.consistency_group"))
        info_layout = QVBoxLayout(info_group)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumWidth(300)
        info_layout.addWidget(self.info_text)
        bottom_layout.addWidget(info_group)

        splitter.addWidget(bottom)
        splitter.setSizes([300, 250])
        layout.addWidget(splitter)

    def set_project(self, project_id, phase=1):
        self.project_id = project_id
        self.phase = phase
        self.refresh()

    def refresh(self):
        if not self.project_id:
            return
        self._vocs = [dict(v) for v in self.db.get_vocs(self.project_id, self.phase)]
        self._build_matrix()
        # Clear stale results from a previously loaded project — they only
        # get recomputed when the user clicks "计算权重" again.
        self._computed_weights = {}
        self.result_table.setRowCount(0)
        self.info_text.clear()

    def _build_matrix(self):
        self.matrix_table.blockSignals(True)
        n = len(self._vocs)
        self.matrix_table.setRowCount(n)
        self.matrix_table.setColumnCount(n)

        labels = [v['name'] for v in self._vocs]
        self.matrix_table.setHorizontalHeaderLabels(labels)
        self.matrix_table.setVerticalHeaderLabels(labels)

        # Load saved comparisons
        comps = self.db.get_ahp_comparisons(self.project_id, self.phase)
        comp_map = {}
        for c in comps:
            comp_map[(c['voc_id_1'], c['voc_id_2'])] = c['value']

        for i in range(n):
            for j in range(n):
                if i == j:
                    item = QTableWidgetItem("1.000")
                    item.setBackground(QColor('#E5E8E8'))
                    item.setForeground(QColor('#555555'))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                elif i < j:
                    vid1, vid2 = self._vocs[i]['id'], self._vocs[j]['id']
                    val = comp_map.get((vid1, vid2), 1.0)
                    item = QTableWidgetItem(f"{val:.3f}")
                    item.setData(Qt.UserRole, (vid1, vid2))
                    item.setForeground(QColor('#1565C0'))
                    item.setFont(QFont("Microsoft YaHei", -1, QFont.Bold))
                else:
                    vid1, vid2 = self._vocs[j]['id'], self._vocs[i]['id']
                    val = comp_map.get((vid1, vid2), 1.0)
                    reciprocal = 1.0 / val if val != 0 else 1.0
                    item = QTableWidgetItem(f"{reciprocal:.3f}")
                    item.setBackground(QColor('#F8F9FA'))
                    item.setForeground(QColor('#777777'))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

                item.setTextAlignment(Qt.AlignCenter)
                self.matrix_table.setItem(i, j, item)

        self.matrix_table.blockSignals(False)
        self.matrix_table.viewport().update()

    def _on_cell_changed(self, row, col):
        if row >= col:
            return
        item = self.matrix_table.item(row, col)
        if not item:
            return
        data = item.data(Qt.UserRole)
        if not data:
            return
        try:
            val = float(item.text())
            if val <= 0:
                val = 1.0
            vid1, vid2 = data
            self.db.set_ahp_comparison(self.project_id, vid1, vid2, val, self.phase)
            # Update reciprocal
            self.matrix_table.blockSignals(True)
            recip_item = self.matrix_table.item(col, row)
            if recip_item:
                recip_item.setText(f"{1.0/val:.3f}")
            self.matrix_table.blockSignals(False)
        except ValueError:
            pass

    def _compute(self):
        n = len(self._vocs)
        if n < 2:
            QMessageBox.information(self, t("common.hint"), t("ahp.need_2_vocs"))
            return

        comps = self.db.get_ahp_comparisons(self.project_id, self.phase)
        comp_dict = {}
        id_list = [v['id'] for v in self._vocs]
        id_to_idx = {vid: i for i, vid in enumerate(id_list)}

        for c in comps:
            i = id_to_idx.get(c['voc_id_1'])
            j = id_to_idx.get(c['voc_id_2'])
            if i is not None and j is not None:
                comp_dict[(i, j)] = c['value']

        matrix = AHPEngine.build_matrix(n, comp_dict)
        result = AHPEngine.compute_weights(matrix)

        # Show results
        self.result_table.setRowCount(n)
        weights = result['weights']
        for i, v in enumerate(self._vocs):
            self.result_table.setItem(i, 0, QTableWidgetItem(v['name']))
            w_item = QTableWidgetItem(f"{weights[i]:.4f}")
            w_item.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(i, 1, w_item)
            p_item = QTableWidgetItem(f"{weights[i]*100:.1f}%")
            p_item.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(i, 2, p_item)

        # Consistency info
        info = f"λmax = {result['lambda_max']:.4f}\n"
        info += f"CI = {result['ci']:.4f}\n"
        info += f"CR = {result['cr']:.4f}\n\n"
        if result['consistent']:
            info += t("ahp.consistent_ok")
            self.info_text.setStyleSheet("color: #27AE60;")
        else:
            info += t("ahp.consistent_fail")
            suggestion = AHPEngine.suggest_fix(matrix)
            if suggestion:
                i, j = suggestion['pair']
                info += t("ahp.suggest_fix", a=self._vocs[i]['name'], b=self._vocs[j]['name'])
                info += t("ahp.current_value", v=f"{suggestion['current_value']:.3f}")
                info += t("ahp.suggested_value", v=f"{suggestion['suggested_value']:.3f}")
            self.info_text.setStyleSheet("color: #E74C3C;")

        self.info_text.setPlainText(info)

        # Store weights for apply
        self._computed_weights = {self._vocs[i]['id']: float(weights[i]) for i in range(n)}

    def _apply_weights(self):
        if not hasattr(self, '_computed_weights') or not self._computed_weights:
            QMessageBox.warning(self, t("common.hint"), t("ahp.click_compute_first"))
            return

        # Build old values lookup
        old_map = {v['id']: v['importance'] for v in self._vocs}

        # Apply: relative weight × 10 → percentage-like scale
        # e.g. weight 0.150 → importance 1.50  (直接使用相对权重×10)
        # This preserves AHP proportional relationships exactly
        details = t("ahp.applied_details_header")
        for vid, w in self._computed_weights.items():
            old_val = old_map.get(vid, '?')
            new_val = round(w * 10, 2)  # 相对权重 × 10
            self.db.update_voc(vid, importance=new_val)
            name = next((v['name'] for v in self._vocs if v['id'] == vid), '?')
            pct = round(w * 100, 1)
            details += f"  {name}: {old_val} → {new_val}  (AHP {pct}%)\n"

        self.weights_computed.emit(self._computed_weights)
        QMessageBox.information(self, t("ahp.applied_title"), details + t("ahp.applied_footer"))


class KanoView(QWidget):
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

        header = QHBoxLayout()
        lbl = QLabel(t("kano.title"))
        lbl.setObjectName("title")
        header.addWidget(lbl)
        header.addStretch()

        btn_auto = QPushButton(t("kano.auto"))
        btn_auto.setObjectName("accent")
        btn_auto.clicked.connect(self._auto_classify)
        header.addWidget(btn_auto)

        btn_chart = QPushButton(t("kano.chart"))
        btn_chart.clicked.connect(self._generate_chart)
        header.addWidget(btn_chart)

        btn_apply = QPushButton(t("kano.apply_adjusted"))
        btn_apply.setObjectName("success")
        btn_apply.setToolTip(t("kano.apply_tooltip"))
        btn_apply.clicked.connect(self._apply_adjusted_importance)
        header.addWidget(btn_apply)
        layout.addLayout(header)

        splitter = QSplitter(Qt.Vertical)

        # Kano classification table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            t("kano.col_name"), t("kano.col_type"), t("kano.col_importance"),
            t("kano.col_multiplier"), t("kano.col_adjusted")
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.setColumnWidth(1, 210)
        self.table.verticalHeader().setDefaultSectionSize(36)
        self.table.setStyleSheet("QTableWidget::item { padding: 0px 3px; font-size: 13px; }"
                                 " QComboBox { min-height: 26px; font-size: 13px; padding: 2px 4px; }")
        self.table.setAlternatingRowColors(True)
        splitter.addWidget(self.table)

        # Chart
        chart_widget = QWidget()
        chart_layout = QVBoxLayout(chart_widget)
        self.fig = Figure(figsize=(8, 5), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.fig)
        chart_layout.addWidget(self.canvas)
        splitter.addWidget(chart_widget)

        splitter.setSizes([300, 300])
        layout.addWidget(splitter)

    def set_project(self, project_id, phase=1):
        self.project_id = project_id
        self.phase = phase
        self.refresh()

    def refresh(self):
        if not self.project_id:
            return
        vocs = self.db.get_vocs(self.project_id, self.phase)
        self.table.setRowCount(len(vocs))

        for i, v in enumerate(vocs):
            name_item = QTableWidgetItem(v['name'])
            name_item.setData(Qt.UserRole, v['id'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 0, name_item)

            # Kano type combo
            kano_combo = QComboBox()
            for k in KANO_TYPES:
                kano_combo.addItem(t(KANO_TYPE_KEYS[k]), k)
            idx = kano_combo.findData(v['kano_type'] or '')
            kano_combo.setCurrentIndex(idx if idx >= 0 else 0)
            kano_combo.currentIndexChanged.connect(lambda _, row=i: self._on_kano_changed(row))
            self.table.setCellWidget(i, 1, kano_combo)

            imp_item = QTableWidgetItem(f"{v['importance']:.2f}")
            imp_item.setTextAlignment(Qt.AlignCenter)
            imp_item.setFlags(imp_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 2, imp_item)

            multiplier = KanoEngine.importance_multiplier(v['kano_type'] or '')
            mult_item = QTableWidgetItem(f"×{multiplier:.1f}")
            mult_item.setTextAlignment(Qt.AlignCenter)
            mult_item.setFlags(mult_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 3, mult_item)

            adj = v['importance'] * multiplier
            adj_item = QTableWidgetItem(f"{adj:.2f}")
            adj_item.setTextAlignment(Qt.AlignCenter)
            adj_item.setFlags(adj_item.flags() & ~Qt.ItemIsEditable)
            adj_item.setFont(QFont("Microsoft YaHei", -1, QFont.Bold))
            self.table.setItem(i, 4, adj_item)

        # Clear the stale quadrant chart from a previously loaded project —
        # it only gets regenerated when the user clicks "生成象限图" again.
        self.fig.clear()
        self.canvas.draw()

    def _on_kano_changed(self, row):
        combo = self.table.cellWidget(row, 1)
        if not combo:
            return
        kano_type = combo.currentData()
        item = self.table.item(row, 0)
        if not item:
            return
        voc_id = item.data(Qt.UserRole)
        self.db.update_voc(voc_id, kano_type=kano_type)

        # Update multiplier and adjusted importance
        v = self.db.conn.execute("SELECT * FROM voc WHERE id=?", (voc_id,)).fetchone()
        multiplier = KanoEngine.importance_multiplier(kano_type)
        self.table.item(row, 3).setText(f"×{multiplier:.1f}")
        adj = (v['importance'] or 3) * multiplier
        self.table.item(row, 4).setText(f"{adj:.2f}")
        self.data_changed.emit()

    def _apply_adjusted_importance(self):
        """Write 调整后重要度 (Ii × Kano系数) back into each VOC's importance.

        Without this, the Kano multiplier is purely a preview — Tai/HOQ and
        everything downstream only ever reads the raw, un-adjusted importance.
        """
        if not self.project_id:
            return
        vocs = self.db.get_vocs(self.project_id, self.phase)
        if not vocs:
            QMessageBox.information(self, t("common.hint"), t("kano.no_voc_data"))
            return
        reply = QMessageBox.question(self, t("kano.confirm_apply_title"), t("kano.confirm_apply_body"),
            QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        details = t("kano.applied_details_header")
        for v in vocs:
            multiplier = KanoEngine.importance_multiplier(v['kano_type'] or '')
            old_val = v['importance'] or 3
            new_val = round(old_val * multiplier, 2)
            self.db.update_voc(v['id'], importance=new_val)
            details += f"  {v['name']}: {old_val} → {new_val}  (×{multiplier})\n"

        self.refresh()
        self.data_changed.emit()
        QMessageBox.information(self, t("kano.applied_title"), details + t("kano.applied_footer"))

    def _auto_classify(self):
        """Simple auto-classification based on keywords in VOC names."""
        vocs = self.db.get_vocs(self.project_id, self.phase)
        classified = 0
        for v in vocs:
            name = v['name'].lower()
            kano = ''
            # Simple keyword-based heuristic
            must_keywords = ['安全', '合规', '标准', '基本', '法规', '必须', '可靠', '耐久']
            attractive_keywords = ['创新', '智能', 'AI', '便捷', '个性', '美观', '惊喜']
            performance_keywords = ['性能', '速度', '效率', '精度', '容量', '功率']

            for kw in must_keywords:
                if kw in name:
                    kano = 'M'
                    break
            if not kano:
                for kw in attractive_keywords:
                    if kw in name:
                        kano = 'A'
                        break
            if not kano:
                for kw in performance_keywords:
                    if kw in name:
                        kano = 'O'
                        break
            if kano and kano != v['kano_type']:
                self.db.update_voc(v['id'], kano_type=kano)
                classified += 1

        self.refresh()
        QMessageBox.information(self, t("kano.auto_done_title"), t("kano.auto_done_body", n=classified))

    def _generate_chart(self):
        vocs = self.db.get_vocs(self.project_id, self.phase)
        if not vocs:
            return

        self.fig.clear()
        ax = self.fig.add_subplot(111)

        kano_colors = {
            'M': '#E74C3C', 'O': '#3498DB', 'A': '#2ECC71',
            'I': '#95A5A6', 'R': '#E67E22', '': '#BDC3C7'
        }

        for v in vocs:
            ktype = v['kano_type'] or ''
            color = kano_colors.get(ktype, '#BDC3C7')
            importance = v['importance'] or 3
            multiplier = KanoEngine.importance_multiplier(ktype)
            ax.scatter(importance, multiplier, c=color, s=100, alpha=0.8, edgecolors='white', linewidth=1)
            ax.annotate(v['name'], (importance, multiplier),
                       fontsize=8, ha='left', va='bottom',
                       xytext=(5, 5), textcoords='offset points')

        # Legend
        for k in KANO_TYPES:
            if k:
                ax.scatter([], [], c=kano_colors[k], s=60, label=t(KANO_TYPE_KEYS[k]))
        ax.legend(loc='upper left', fontsize=9)

        ax.set_xlabel(t("kano.chart_xlabel"), fontsize=11)
        ax.set_ylabel(t("kano.chart_ylabel"), fontsize=11)
        ax.set_title(t("kano.chart_title"), fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
        self.fig.tight_layout()
        self.canvas.draw()


class ParetoView(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.project_id = None
        self.phase = 1
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()
        lbl = QLabel(t("pareto.title"))
        lbl.setObjectName("title")
        header.addWidget(lbl)
        header.addStretch()

        self.sort_combo = QComboBox()
        self.sort_combo.addItems([t("pareto.sort_abs"), t("pareto.sort_rel"), t("pareto.sort_weighted")])
        self.sort_combo.currentIndexChanged.connect(self._generate_chart)
        header.addWidget(QLabel(t("pareto.sort_by")))
        header.addWidget(self.sort_combo)

        btn_gen = QPushButton(t("pareto.generate"))
        btn_gen.clicked.connect(self._generate_chart)
        header.addWidget(btn_gen)
        layout.addLayout(header)

        self.fig = Figure(figsize=(10, 5), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.fig)
        layout.addWidget(self.canvas)

        # Summary
        self.summary_label = QLabel("")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet("padding: 10px; background: #EBF5FB; border-radius: 6px; font-size: 13px;")
        layout.addWidget(self.summary_label)

    def set_project(self, project_id, phase=1):
        self.project_id = project_id
        self.phase = phase
        # Clear the stale chart from a previously loaded project — it only
        # gets regenerated when the user clicks "生成Pareto图" again.
        self.fig.clear()
        self.canvas.draw()
        self.summary_label.setText("")

    def _generate_chart(self):
        if not self.project_id:
            return

        vocs = [dict(v) for v in self.db.get_vocs(self.project_id, self.phase)]
        ctqs = [dict(c) for c in self.db.get_ctqs(self.project_id, self.phase)]
        rels = [dict(r) for r in self.db.get_relationships(self.project_id, self.phase)]

        if not ctqs:
            QMessageBox.information(self, t("common.hint"), t("pareto.need_ctq"))
            return

        importance = HOQEngine.compute_importance(vocs, ctqs, rels)

        sort_key = ['absolute_importance', 'relative_importance', 'weighted_importance'][self.sort_combo.currentIndex()]

        # Sort by chosen metric
        sorted_items = sorted(
            [(c, importance.get(c['id'], {})) for c in ctqs],
            key=lambda x: x[1].get(sort_key, 0),
            reverse=True
        )

        names = [item[0]['name'] for item in sorted_items]
        values = [item[1].get(sort_key, 0) for item in sorted_items]
        total = sum(values) if values else 1
        cumulative = np.cumsum(values) / total * 100 if total > 0 else np.zeros(len(values))

        self.fig.clear()
        ax1 = self.fig.add_subplot(111)

        # Bar chart
        n = len(names)
        top20_idx = max(1, int(n * 0.2))
        bar_colors = [COLORS['accent'] if i < top20_idx else COLORS['primary_light'] for i in range(n)]
        bars = ax1.bar(range(n), values, color=bar_colors, alpha=0.85, edgecolor='white', linewidth=0.5)

        ax1.set_ylabel(self.sort_combo.currentText(), fontsize=11, color=COLORS['primary'])
        ax1.set_xticks(range(n))
        ax1.set_xticklabels(names, rotation=45, ha='right', fontsize=9)

        # Cumulative line
        ax2 = ax1.twinx()
        ax2.plot(range(n), cumulative, 'o-', color=COLORS['danger'], linewidth=2, markersize=5)
        ax2.set_ylabel(t("pareto.cumulative_pct"), fontsize=11, color=COLORS['danger'])
        ax2.set_ylim(0, 110)
        ax2.axhline(y=80, color='gray', linestyle='--', alpha=0.5, label=t("pareto.line_80"))

        ax1.set_title(t("pareto.chart_title"), fontsize=14, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        self.fig.tight_layout()
        self.canvas.draw()

        # Summary
        top_names = names[:top20_idx]
        self.summary_label.setText(t("pareto.summary", n=top20_idx, names=', '.join(top_names),
                                      pct=f"{cumulative[top20_idx-1]:.1f}"))
