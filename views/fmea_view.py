"""
FMEA Module - Failure Mode and Effects Analysis
DFMEA/PFMEA worksheet with RPN calculation, color-coded risk, CTQ import from HOQ.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QGroupBox, QMessageBox,
    QHeaderView, QAbstractItemView, QSpinBox, QFileDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

from utils.i18n import t


class FMEAView(QWidget):
    data_changed = Signal()

    @property
    def COLUMNS(self):
        return [
            t("fmea.col_item"), t("fmea.col_failure_mode"), t("fmea.col_failure_effect"), t("fmea.col_severity"),
            t("fmea.col_failure_cause"), t("fmea.col_occurrence"), t("fmea.col_control"), t("fmea.col_detection"),
            t("fmea.col_rpn"), t("fmea.col_risk_level"), t("fmea.col_suggested"), t("fmea.col_responsible")
        ]

    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.project_id = None
        self._data = []  # list of row dicts
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()
        lbl = QLabel(t("fmea.title"))
        lbl.setObjectName("title")
        header.addWidget(lbl)
        header.addStretch()

        self.type_combo = QComboBox()
        self.type_combo.addItems([t("fmea.type_dfmea"), t("fmea.type_pfmea")])
        header.addWidget(self.type_combo)

        btn_add = QPushButton(t("fmea.add_row"))
        btn_add.clicked.connect(self._add_row)
        header.addWidget(btn_add)

        btn_import = QPushButton(t("fmea.import_hoq"))
        btn_import.setObjectName("accent")
        btn_import.clicked.connect(self._import_from_hoq)
        header.addWidget(btn_import)

        btn_del = QPushButton(t("fmea.delete_row"))
        btn_del.setObjectName("danger")
        btn_del.clicked.connect(self._delete_row)
        header.addWidget(btn_del)

        btn_export = QPushButton(t("fmea.export_csv"))
        btn_export.setObjectName("secondary")
        btn_export.clicked.connect(self._export_csv)
        header.addWidget(btn_export)
        layout.addLayout(header)

        hint = QLabel(t("fmea.hint"))
        hint.setStyleSheet("color: #7F8C8D; font-size: 11px;")
        layout.addWidget(hint)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.verticalHeader().setDefaultSectionSize(34)
        self.table.setStyleSheet("QTableWidget::item { padding: 0px 3px; font-size: 13px; }")
        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(4, 150)
        self.table.setColumnWidth(6, 150)
        self.table.setColumnWidth(10, 150)
        self.table.setAlternatingRowColors(True)
        self.table.cellChanged.connect(self._on_cell_changed)
        layout.addWidget(self.table)

        # Summary
        self.summary = QLabel("")
        self.summary.setStyleSheet("padding: 10px; background: #EBF5FB; border-radius: 6px;")
        layout.addWidget(self.summary)

    # Maps table column index -> fmea_item db column (RPN/risk level are derived, not stored)
    _DB_COLS = {0: "item_name", 1: "failure_mode", 2: "failure_effect", 3: "severity",
                4: "failure_cause", 5: "occurrence", 6: "control_measure", 7: "detection",
                10: "suggested_action", 11: "responsible"}

    def set_project(self, project_id, phase=1):
        self.project_id = project_id
        self.refresh()

    def refresh(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        self.table.blockSignals(False)
        if not self.db or not self.project_id:
            return
        items = self.db.get_fmea_items(self.project_id)
        for it in items:
            self._add_row_from_db(dict(it))
        self._update_summary()

    def _add_row_from_db(self, it):
        row = self.table.rowCount()
        self.table.blockSignals(True)
        self.table.insertRow(row)
        values = [it.get("item_name", ""), it.get("failure_mode", ""), it.get("failure_effect", ""),
                  str(it.get("severity", 5)), it.get("failure_cause", ""), str(it.get("occurrence", 5)),
                  it.get("control_measure", ""), str(it.get("detection", 5)), "", "",
                  it.get("suggested_action", ""), it.get("responsible", "")]
        for col, val in enumerate(values):
            item = QTableWidgetItem(str(val) if val is not None else "")
            item.setTextAlignment(Qt.AlignCenter if col in (3, 5, 7, 8, 9) else Qt.AlignLeft | Qt.AlignVCenter)
            if col == 0:
                item.setData(Qt.UserRole, it["id"])
            self.table.setItem(row, col, item)
        self.table.blockSignals(False)
        self._recalc_row(row)

    def _add_row(self, item_name="", cause=""):
        row = self.table.rowCount()
        self.table.blockSignals(True)
        self.table.insertRow(row)
        defaults = [item_name, "", "", "5", cause, "5", "", "5", "", "", "", ""]
        item_id = None
        if self.db and self.project_id:
            item_id = self.db.add_fmea_item(
                self.project_id, item_name=item_name, severity=5,
                failure_cause=cause, occurrence=5, detection=5, sort_order=row)
        for col, val in enumerate(defaults):
            item = QTableWidgetItem(val)
            item.setTextAlignment(Qt.AlignCenter if col in (3,5,7,8,9) else Qt.AlignLeft|Qt.AlignVCenter)
            if col == 0:
                item.setData(Qt.UserRole, item_id)
            self.table.setItem(row, col, item)
        self.table.blockSignals(False)
        self._recalc_row(row)

    def _delete_row(self):
        row = self.table.currentRow()
        if row >= 0:
            name_item = self.table.item(row, 0)
            item_id = name_item.data(Qt.UserRole) if name_item else None
            if item_id and self.db:
                self.db.delete_fmea_item(item_id)
            self.table.removeRow(row)
            self._update_summary()

    def _on_cell_changed(self, row, col):
        if col in (3, 5, 7):  # S, O, D columns
            self._recalc_row(row)
        self._save_row(row, col)

    def _save_row(self, row, col):
        if not self.db or not self.project_id:
            return
        db_col = self._DB_COLS.get(col)
        if not db_col:
            return
        name_item = self.table.item(row, 0)
        item = self.table.item(row, col)
        if not name_item or not item:
            return
        item_id = name_item.data(Qt.UserRole)
        text = item.text()
        if col in (3, 5, 7):
            try:
                text = max(1, min(10, int(text or 5)))
            except ValueError:
                text = 5
        if item_id:
            self.db.update_fmea_item(item_id, **{db_col: text})
        elif self.db and self.project_id:
            # Row created before a project was open — persist it now.
            new_id = self.db.add_fmea_item(self.project_id, sort_order=row, **{db_col: text})
            name_item.setData(Qt.UserRole, new_id)

    def _recalc_row(self, row):
        try:
            s = int(self.table.item(row, 3).text() or 1)
            o = int(self.table.item(row, 5).text() or 1)
            d = int(self.table.item(row, 7).text() or 1)
            s = max(1, min(10, s))
            o = max(1, min(10, o))
            d = max(1, min(10, d))
        except (ValueError, AttributeError):
            return

        rpn = s * o * d

        # RPN cell
        rpn_item = QTableWidgetItem(str(rpn))
        rpn_item.setTextAlignment(Qt.AlignCenter)
        rpn_item.setFont(QFont("Microsoft YaHei", -1, QFont.Bold))
        rpn_item.setFlags(rpn_item.flags() & ~Qt.ItemIsEditable)

        # Risk level
        if rpn >= 200:
            level, color = t("fmea.risk_high"), "#E74C3C"
            rpn_item.setBackground(QColor("#FADBD8"))
        elif rpn >= 100:
            level, color = t("fmea.risk_mid"), "#E67E22"
            rpn_item.setBackground(QColor("#FDEBD0"))
        elif rpn >= 50:
            level, color = t("fmea.risk_low"), "#F39C12"
            rpn_item.setBackground(QColor("#FEF9E7"))
        else:
            level, color = t("fmea.risk_ok"), "#27AE60"
            rpn_item.setBackground(QColor("#D5F5E3"))

        self.table.blockSignals(True)
        self.table.setItem(row, 8, rpn_item)

        level_item = QTableWidgetItem(level)
        level_item.setTextAlignment(Qt.AlignCenter)
        level_item.setForeground(QColor(color))
        level_item.setFont(QFont("Microsoft YaHei", -1, QFont.Bold))
        level_item.setFlags(level_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, 9, level_item)
        self.table.blockSignals(False)

        self._update_summary()

    def _update_summary(self):
        total = self.table.rowCount()
        high = mid = low = ok = 0
        for row in range(total):
            item = self.table.item(row, 8)
            if item and item.text():
                try:
                    rpn = int(item.text())
                    if rpn >= 200: high += 1
                    elif rpn >= 100: mid += 1
                    elif rpn >= 50: low += 1
                    else: ok += 1
                except: pass
        self.summary.setText(t("fmea.summary", total=total, high=high, mid=mid, low=low, ok=ok))

    def _import_from_hoq(self):
        if not self.db or not self.project_id:
            QMessageBox.warning(self, t("common.hint"), t("fmea.need_project"))
            return
        from engines.compute import HOQEngine
        vocs = [dict(v) for v in self.db.get_vocs(self.project_id, 1)]
        ctqs = [dict(c) for c in self.db.get_ctqs(self.project_id, 1)]
        rels = [dict(r) for r in self.db.get_relationships(self.project_id, 1)]
        if not ctqs:
            QMessageBox.information(self, t("common.hint"), t("fmea.need_ctq"))
            return
        importance = HOQEngine.compute_importance(vocs, ctqs, rels)
        # Import top CTQs as FMEA items
        sorted_ctqs = sorted(ctqs, key=lambda c: importance.get(c['id'], {}).get('rank', 999))
        for c in sorted_ctqs:
            imp = importance.get(c['id'], {})
            self._add_row(
                item_name=c['name'],
                cause=t("fmea.import_cause", rank=imp.get('rank', '?'))
            )
        QMessageBox.information(self, t("fmea.import_done_title"), t("fmea.import_done_body", n=len(ctqs)))

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, t("fmea.dlg_export_title"), "FMEA_Report.csv", t("common.csv_filter"))
        if not path:
            return
        import csv
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(self.COLUMNS)
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else "")
                writer.writerow(row_data)
        QMessageBox.information(self, t("common.success"), t("fmea.export_success", path=path))
