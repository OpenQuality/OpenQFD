"""
DSM Module - Design Structure Matrix
NxN dependency matrix for architecture analysis, clustering, sequencing.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QGroupBox, QMessageBox,
    QHeaderView, QAbstractItemView, QLineEdit, QInputDialog, QFileDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

from utils.i18n import t


class DSMView(QWidget):
    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.project_id = None
        self._elements = []    # list of element names
        self._element_ids = [] # db ids aligned with self._elements, by index
        self._matrix = {}      # {(i,j): str}  dependency marker
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()
        lbl = QLabel(t("dsm.title"))
        lbl.setObjectName("title")
        header.addWidget(lbl)
        header.addStretch()

        btn_add = QPushButton(t("dsm.add_element"))
        btn_add.clicked.connect(self._add_element)
        header.addWidget(btn_add)

        btn_import = QPushButton(t("dsm.import_ctq"))
        btn_import.setObjectName("accent")
        btn_import.clicked.connect(self._import_from_ctq)
        header.addWidget(btn_import)

        btn_del = QPushButton(t("dsm.delete_last"))
        btn_del.setObjectName("danger")
        btn_del.clicked.connect(self._delete_last)
        header.addWidget(btn_del)

        btn_clear = QPushButton(t("dsm.clear_matrix"))
        btn_clear.setObjectName("secondary")
        btn_clear.clicked.connect(self._clear_matrix)
        header.addWidget(btn_clear)

        btn_export = QPushButton(t("dsm.export_csv"))
        btn_export.setObjectName("secondary")
        btn_export.clicked.connect(self._export_csv)
        header.addWidget(btn_export)
        layout.addLayout(header)

        hint = QLabel(t("dsm.hint"))
        hint.setStyleSheet("color: #7F8C8D; font-size: 11px;")
        layout.addWidget(hint)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(False)
        self.table.cellClicked.connect(self._on_cell_clicked)
        self.table.setStyleSheet("""
            QTableWidget { gridline-color: #BDBDBD; font-size: 13px; }
            QTableWidget::item { padding: 0px 3px; }
            QHeaderView::section { background: #EBF5FB; font-weight: bold;
                border: 1px solid #BDBDBD; padding: 4px; font-size: 11px; }
        """)
        layout.addWidget(self.table)

        # Analysis summary
        self.summary_group = QGroupBox(t("dsm.analysis_group"))
        sg = QVBoxLayout(self.summary_group)
        self.analysis_label = QLabel("")
        self.analysis_label.setWordWrap(True)
        self.analysis_label.setStyleSheet("font-size: 13px; line-height: 1.6;")
        sg.addWidget(self.analysis_label)

        btn_analyze = QPushButton(t("dsm.analyze"))
        btn_analyze.clicked.connect(self._analyze)
        sg.addWidget(btn_analyze)
        layout.addWidget(self.summary_group)

    def set_project(self, project_id, phase=1):
        self.project_id = project_id
        self.refresh()

    def refresh(self):
        self._elements = []
        self._element_ids = []
        self._matrix = {}
        if self.db and self.project_id:
            elements = self.db.get_dsm_elements(self.project_id)
            self._elements = [e['name'] for e in elements]
            self._element_ids = [e['id'] for e in elements]
            id_to_idx = {eid: i for i, eid in enumerate(self._element_ids)}
            for dep in self.db.get_dsm_dependencies(self.project_id):
                i = id_to_idx.get(dep['from_id'])
                j = id_to_idx.get(dep['to_id'])
                if i is not None and j is not None:
                    self._matrix[(i, j)] = dep['marker']
        self._refresh_table()

    def _add_element(self):
        name, ok = QInputDialog.getText(self, t("dsm.add_element_title"), t("dsm.add_element_label"))
        if ok and name.strip():
            self._add_element_named(name.strip())
            self._refresh_table()

    def _add_element_named(self, name):
        element_id = None
        if self.db and self.project_id:
            element_id = self.db.add_dsm_element(self.project_id, name, sort_order=len(self._elements))
        self._elements.append(name)
        self._element_ids.append(element_id)

    def _import_from_ctq(self):
        if not self.db or not self.project_id:
            QMessageBox.warning(self, t("common.hint"), t("dsm.need_project"))
            return
        ctqs = self.db.get_ctqs(self.project_id, 1)
        if not ctqs:
            QMessageBox.information(self, t("common.hint"), t("dsm.need_ctq"))
            return
        for c in ctqs:
            if c['name'] not in self._elements:
                self._add_element_named(c['name'])
        self._refresh_table()
        QMessageBox.information(self, t("dsm.import_done_title"), t("dsm.import_done_body", n=len(ctqs)))

    def _delete_last(self):
        if self._elements:
            self._elements.pop()
            removed_id = self._element_ids.pop()
            if removed_id and self.db:
                self.db.delete_dsm_element(removed_id)  # cascades dependencies
            # Clean matrix entries for removed element
            n = len(self._elements)
            new_matrix = {}
            for (i, j), v in self._matrix.items():
                if i < n and j < n:
                    new_matrix[(i, j)] = v
            self._matrix = new_matrix
            self._refresh_table()

    def _clear_matrix(self):
        self._matrix.clear()
        if self.db and self.project_id:
            self.db.clear_dsm_dependencies(self.project_id)
        self._refresh_table()

    def _refresh_table(self):
        n = len(self._elements)
        self.table.setRowCount(n)
        self.table.setColumnCount(n)
        self.table.setHorizontalHeaderLabels(self._elements)
        self.table.setVerticalHeaderLabels(self._elements)
        self.table.horizontalHeader().setDefaultSectionSize(60)
        self.table.verticalHeader().setDefaultSectionSize(32)

        for i in range(n):
            for j in range(n):
                if i == j:
                    item = QTableWidgetItem("■")
                    item.setBackground(QColor("#B0BEC5"))
                    item.setForeground(QColor("#546E7A"))
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable)
                else:
                    dep = self._matrix.get((i, j), "")
                    item = QTableWidgetItem(dep)
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    if dep == "X":
                        item.setBackground(QColor("#1565C0"))
                        item.setForeground(QColor(Qt.white))
                        item.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
                    elif dep == "?":
                        item.setBackground(QColor("#FFF176"))
                self.table.setItem(i, j, item)

    def _on_cell_clicked(self, row, col):
        if row == col:
            return
        n = len(self._elements)
        if row >= n or col >= n:
            return
        current = self._matrix.get((row, col), "")
        cycle = ["", "X", "?"]  # empty -> dependency -> uncertain -> empty
        idx = cycle.index(current) if current in cycle else 0
        new_val = cycle[(idx + 1) % len(cycle)]
        if new_val:
            self._matrix[(row, col)] = new_val
        elif (row, col) in self._matrix:
            del self._matrix[(row, col)]

        if self.db and self.project_id:
            from_id, to_id = self._element_ids[row], self._element_ids[col]
            if from_id and to_id:
                if new_val:
                    self.db.set_dsm_dependency(self.project_id, from_id, to_id, new_val)
                else:
                    self.db.delete_dsm_dependency(self.project_id, from_id, to_id)
        self._refresh_table()

    def _analyze(self):
        n = len(self._elements)
        if n == 0:
            self.analysis_label.setText(t("dsm.need_elements"))
            return

        # Count dependencies
        dep_out = [0] * n  # how many others this element depends on
        dep_in = [0] * n   # how many others depend on this element
        for (i, j), v in self._matrix.items():
            if v == "X":
                dep_out[i] += 1
                dep_in[j] += 1

        total_deps = sum(dep_out)
        density = total_deps / (n * (n-1)) * 100 if n > 1 else 0

        # Find most dependent and most depended-on
        if n > 0:
            most_out = max(range(n), key=lambda i: dep_out[i])
            most_in = max(range(n), key=lambda i: dep_in[i])
        else:
            most_out = most_in = 0

        # Find potential clusters (bidirectional dependencies)
        clusters = []
        for i in range(n):
            for j in range(i+1, n):
                if self._matrix.get((i,j)) == "X" and self._matrix.get((j,i)) == "X":
                    clusters.append(f"{self._elements[i]} ↔ {self._elements[j]}")

        # Find independent elements
        independent = [self._elements[i] for i in range(n) if dep_out[i] == 0 and dep_in[i] == 0]

        analysis = t("dsm.analysis_size", n=n)
        analysis += t("dsm.analysis_total", n=total_deps)
        analysis += t("dsm.analysis_density", pct=f"{density:.1f}")

        if n > 0:
            analysis += t("dsm.analysis_most_out", name=self._elements[most_out], n=dep_out[most_out])
            analysis += t("dsm.analysis_most_in", name=self._elements[most_in], n=dep_in[most_in])

        if clusters:
            analysis += t("dsm.analysis_clusters", list='、'.join(clusters))
            analysis += f"<span style='color:#E74C3C;'>{t('dsm.analysis_clusters_note')}</span>"

        if independent:
            analysis += t("dsm.analysis_independent", list='、'.join(independent))
            analysis += f"<span style='color:#27AE60;'>{t('dsm.analysis_independent_note')}</span>"

        self.analysis_label.setText(analysis)

    def _export_csv(self):
        if not self._elements:
            return
        path, _ = QFileDialog.getSaveFileName(self, t("dsm.dlg_export_title"), "DSM_Matrix.csv", t("common.csv_filter"))
        if not path:
            return
        import csv
        n = len(self._elements)
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([""] + self._elements)
            for i in range(n):
                row = [self._elements[i]]
                for j in range(n):
                    if i == j:
                        row.append("■")
                    else:
                        row.append(self._matrix.get((i,j), ""))
                writer.writerow(row)
        QMessageBox.information(self, t("common.success"), t("dsm.export_success", path=path))
