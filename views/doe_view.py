"""
DOE Module - Design of Experiments
Full factorial / fractional factorial design, experiment table generation.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QGroupBox, QMessageBox,
    QHeaderView, QAbstractItemView, QSpinBox, QLineEdit,
    QFormLayout, QSplitter, QFileDialog, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
import itertools

from utils.i18n import t


class DOEView(QWidget):
    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self._factors = []  # list of {'name': str, 'levels': [str]}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        lbl = QLabel(t("doe.title"))
        lbl.setObjectName("title")
        lbl.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        layout.addWidget(lbl)

        hint = QLabel(t("doe.hint"))
        hint.setStyleSheet("color: #7F8C8D; font-size: 11px;")
        hint.setWordWrap(True)
        hint.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        layout.addWidget(hint)

        splitter = QSplitter(Qt.Horizontal)

        # Left: Factor definition
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0,0,0,0)

        factor_group = QGroupBox(t("doe.factor_group"))
        fg = QVBoxLayout(factor_group)

        add_row = QHBoxLayout()
        self.factor_name = QLineEdit()
        self.factor_name.setPlaceholderText(t("doe.factor_name_placeholder"))
        add_row.addWidget(self.factor_name)
        self.factor_levels = QLineEdit()
        self.factor_levels.setPlaceholderText(t("doe.factor_levels_placeholder"))
        add_row.addWidget(self.factor_levels)
        btn_add = QPushButton(t("doe.add_factor"))
        btn_add.clicked.connect(self._add_factor)
        add_row.addWidget(btn_add)
        fg.addLayout(add_row)

        self.factor_table = QTableWidget()
        self.factor_table.setColumnCount(3)
        self.factor_table.setHorizontalHeaderLabels([t("doe.col_factor_name"), t("doe.col_level_count"), t("doe.col_level_values")])
        self.factor_table.verticalHeader().setDefaultSectionSize(34)
        self.factor_table.setStyleSheet("QTableWidget::item { padding: 0px 3px; font-size: 13px; }")
        self.factor_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.factor_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.factor_table.setColumnWidth(0, 120)
        self.factor_table.setColumnWidth(1, 60)
        fg.addWidget(self.factor_table)

        btn_row = QHBoxLayout()
        btn_del = QPushButton(t("doe.delete_factor"))
        btn_del.setObjectName("danger")
        btn_del.clicked.connect(self._delete_factor)
        btn_row.addWidget(btn_del)

        btn_gen = QPushButton(t("doe.generate"))
        btn_gen.setObjectName("success")
        btn_gen.clicked.connect(self._generate_design)
        btn_row.addWidget(btn_gen)
        fg.addLayout(btn_row)

        left_layout.addWidget(factor_group)

        # Design type
        type_group = QGroupBox(t("doe.design_type_group"))
        tg = QHBoxLayout(type_group)
        self.design_type = QComboBox()
        self.design_type.addItems([t("doe.full_factorial"), t("doe.l8_orthogonal")])
        tg.addWidget(self.design_type)
        self.run_info = QLabel(t("doe.run_count", n=0))
        self.run_info.setStyleSheet("font-weight: bold; color: #1565C0;")
        tg.addWidget(self.run_info)
        left_layout.addWidget(type_group)

        splitter.addWidget(left)

        # Right: Experiment table
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0,0,0,0)

        exp_header = QHBoxLayout()
        exp_header.addWidget(QLabel(t("doe.exp_table_title")))
        btn_export = QPushButton(t("doe.export_csv"))
        btn_export.setObjectName("secondary")
        btn_export.clicked.connect(self._export_csv)
        exp_header.addWidget(btn_export)
        exp_header.addStretch()
        right_layout.addLayout(exp_header)

        self.exp_table = QTableWidget()
        self.exp_table.setAlternatingRowColors(True)
        self.exp_table.verticalHeader().setDefaultSectionSize(34)
        self.exp_table.setStyleSheet("QTableWidget::item { padding: 0px 3px; font-size: 13px; }")
        right_layout.addWidget(self.exp_table)

        splitter.addWidget(right)
        splitter.setSizes([400, 500])
        layout.addWidget(splitter, 1)

    def _add_factor(self):
        name = self.factor_name.text().strip()
        levels_str = self.factor_levels.text().strip()
        if not name or not levels_str:
            QMessageBox.warning(self, t("common.hint"), t("doe.need_name_and_levels"))
            return
        levels = [l.strip() for l in levels_str.split(",") if l.strip()]
        if len(levels) < 2:
            QMessageBox.warning(self, t("common.hint"), t("doe.need_2_levels"))
            return
        if len(self._factors) >= 5:
            QMessageBox.warning(self, t("common.hint"), t("doe.max_5_factors"))
            return

        self._factors.append({"name": name, "levels": levels})
        self._refresh_factor_table()
        self.factor_name.clear()
        self.factor_levels.clear()

    def _delete_factor(self):
        row = self.factor_table.currentRow()
        if 0 <= row < len(self._factors):
            self._factors.pop(row)
            self._refresh_factor_table()

    def _refresh_factor_table(self):
        self.factor_table.setRowCount(len(self._factors))
        total_runs = 1
        for i, f in enumerate(self._factors):
            self.factor_table.setItem(i, 0, QTableWidgetItem(f["name"]))
            self.factor_table.setItem(i, 1, QTableWidgetItem(str(len(f["levels"]))))
            self.factor_table.setItem(i, 2, QTableWidgetItem(", ".join(f["levels"])))
            total_runs *= len(f["levels"])
        self.run_info.setText(t("doe.run_count", n=total_runs) if self._factors else t("doe.run_count", n=0))

    def _generate_design(self):
        if not self._factors:
            QMessageBox.warning(self, t("common.hint"), t("doe.need_factors"))
            return

        if self.design_type.currentIndex() == 0:
            self._full_factorial()
        else:
            self._orthogonal_l8()

    def _full_factorial(self):
        """Generate full factorial design."""
        all_levels = [f["levels"] for f in self._factors]
        runs = list(itertools.product(*all_levels))

        n_factors = len(self._factors)
        cols = [t("doe.col_run_no")] + [f["name"] for f in self._factors] + [t("doe.col_response"), t("doe.col_remarks")]
        self.exp_table.setColumnCount(len(cols))
        self.exp_table.setHorizontalHeaderLabels(cols)
        self.exp_table.setRowCount(len(runs))

        for i, run in enumerate(runs):
            # Run number
            num_item = QTableWidgetItem(str(i + 1))
            num_item.setTextAlignment(Qt.AlignCenter)
            num_item.setBackground(QColor("#EBF5FB"))
            num_item.setFlags(num_item.flags() & ~Qt.ItemIsEditable)
            self.exp_table.setItem(i, 0, num_item)
            # Factor values
            for j, val in enumerate(run):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                # Alternate colors per factor level
                self.exp_table.setItem(i, 1 + j, item)
            # Response (empty for user to fill)
            self.exp_table.setItem(i, n_factors + 1, QTableWidgetItem(""))
            self.exp_table.setItem(i, n_factors + 2, QTableWidgetItem(""))

        self.exp_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.run_info.setText(t("doe.full_factorial_result", n=len(runs)))

    def _orthogonal_l8(self):
        """Generate L8(2^7) orthogonal array for 2-level factors."""
        # Standard L8 orthogonal array
        L8 = [
            [1,1,1,1,1,1,1],
            [1,1,1,2,2,2,2],
            [1,2,2,1,1,2,2],
            [1,2,2,2,2,1,1],
            [2,1,2,1,2,1,2],
            [2,1,2,2,1,2,1],
            [2,2,1,1,2,2,1],
            [2,2,1,2,1,1,2],
        ]
        n_factors = min(len(self._factors), 7)
        cols = [t("doe.col_run_no")] + [self._factors[i]["name"] for i in range(n_factors)] + [t("doe.col_response")]
        self.exp_table.setColumnCount(len(cols))
        self.exp_table.setHorizontalHeaderLabels(cols)
        self.exp_table.setRowCount(8)

        for i, row in enumerate(L8):
            self.exp_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            for j in range(n_factors):
                level_idx = row[j] - 1  # L8 uses 1-based
                levels = self._factors[j]["levels"]
                val = levels[min(level_idx, len(levels)-1)]
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.exp_table.setItem(i, 1 + j, item)
            self.exp_table.setItem(i, n_factors + 1, QTableWidgetItem(""))

        self.exp_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.run_info.setText(t("doe.l8_result", n=n_factors))

    def _export_csv(self):
        if self.exp_table.rowCount() == 0:
            QMessageBox.warning(self, t("common.hint"), t("doe.need_design_first"))
            return
        path, _ = QFileDialog.getSaveFileName(self, t("doe.dlg_export_title"), "DOE_Design.csv", t("common.csv_filter"))
        if not path:
            return
        import csv
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            headers = [self.exp_table.horizontalHeaderItem(c).text()
                      for c in range(self.exp_table.columnCount())]
            writer.writerow(headers)
            for r in range(self.exp_table.rowCount()):
                row = [self.exp_table.item(r, c).text() if self.exp_table.item(r, c) else ""
                       for c in range(self.exp_table.columnCount())]
                writer.writerow(row)
        QMessageBox.information(self, t("common.success"), t("doe.export_success", path=path))
