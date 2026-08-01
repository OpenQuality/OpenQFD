"""
CTQ (Critical To Quality) Management View
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QDoubleSpinBox,
    QGroupBox, QFormLayout, QMessageBox, QHeaderView, QAbstractItemView,
    QSplitter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from views.styles import DIRECTION_LABELS, DIRECTION_SYMBOLS, DIRECTION_KEYS, COLORS
from utils.i18n import t


class CTQManagerView(QWidget):
    data_changed = Signal()

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.project_id = None
        self.phase = 1
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        splitter = QSplitter(Qt.Horizontal)

        # Left: Table
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)

        header = QHBoxLayout()
        lbl = QLabel(t("ctq.title"))
        lbl.setObjectName("title")
        header.addWidget(lbl)
        header.addStretch()

        btn_add = QPushButton(t("ctq.add"))
        btn_add.clicked.connect(self._add_ctq)
        header.addWidget(btn_add)

        btn_del = QPushButton(t("ctq.delete"))
        btn_del.setObjectName("danger")
        btn_del.clicked.connect(self._delete_ctq)
        header.addWidget(btn_del)
        left_layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            t("ctq.col_name"), t("ctq.col_unit"), t("ctq.col_direction"), t("ctq.col_current"),
            t("ctq.col_target"), t("ctq.col_difficulty"), t("ctq.col_sort")
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 7):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setDefaultSectionSize(32)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        # Read-only: edits happen only through the detail editor on the right.
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.currentCellChanged.connect(self._on_row_changed)
        left_layout.addWidget(self.table)

        # Bottom buttons
        bottom_layout = QHBoxLayout()
        btn_up = QPushButton(t("common.up"))
        btn_up.setObjectName("secondary")
        btn_up.clicked.connect(lambda: self._move_ctq(-1))
        bottom_layout.addWidget(btn_up)

        btn_down = QPushButton(t("common.down"))
        btn_down.setObjectName("secondary")
        btn_down.clicked.connect(lambda: self._move_ctq(1))
        bottom_layout.addWidget(btn_down)

        bottom_layout.addStretch()
        self.count_label = QLabel(t("ctq.count", n=0))
        self.count_label.setObjectName("subtitle")
        bottom_layout.addWidget(self.count_label)
        left_layout.addLayout(bottom_layout)

        splitter.addWidget(left)

        # Right: Detail editor
        right = QWidget()
        right.setMinimumWidth(320)
        right.setMaximumWidth(400)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        detail_label = QLabel(t("ctq.detail"))
        detail_label.setObjectName("title")
        right_layout.addWidget(detail_label)

        form_group = QGroupBox(t("voc.basic_info"))
        form = QFormLayout(form_group)

        self.edit_name = QLineEdit()
        self.edit_name.setPlaceholderText(t("ctq.name_placeholder"))
        form.addRow(t("voc.name"), self.edit_name)

        self.edit_unit = QLineEdit()
        self.edit_unit.setPlaceholderText(t("ctq.unit_placeholder"))
        form.addRow(t("ctq.unit"), self.edit_unit)

        self.edit_direction = QComboBox()
        for k in DIRECTION_LABELS:
            self.edit_direction.addItem(t(DIRECTION_KEYS[k]), k)
        form.addRow(t("ctq.direction"), self.edit_direction)

        self.edit_current = QLineEdit()
        self.edit_current.setPlaceholderText(t("ctq.current_placeholder"))
        form.addRow(t("ctq.current"), self.edit_current)

        self.edit_target = QLineEdit()
        self.edit_target.setPlaceholderText(t("ctq.target_placeholder"))
        form.addRow(t("ctq.target"), self.edit_target)

        self.edit_difficulty = QDoubleSpinBox()
        self.edit_difficulty.setRange(1.0, 5.0)
        self.edit_difficulty.setSingleStep(0.5)
        self.edit_difficulty.setDecimals(1)
        self.edit_difficulty.setValue(3.0)
        self.edit_difficulty.setToolTip(t("ctq.difficulty_tooltip"))
        form.addRow(t("ctq.difficulty"), self.edit_difficulty)

        right_layout.addWidget(form_group)

        save_btn = QPushButton(t("voc.save"))
        save_btn.setObjectName("success")
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self._save_current)
        right_layout.addWidget(save_btn)

        right_layout.addStretch()
        splitter.addWidget(right)
        splitter.setSizes([600, 350])
        layout.addWidget(splitter)

    def set_project(self, project_id, phase=1):
        self.project_id = project_id
        self.phase = phase
        self.refresh()

    def refresh(self):
        if not self.project_id:
            return
        ctqs = self.db.get_ctqs(self.project_id, self.phase)
        self.table.setRowCount(len(ctqs))
        for i, c in enumerate(ctqs):
            name_item = QTableWidgetItem(c['name'])
            name_item.setData(Qt.UserRole, c['id'])
            self.table.setItem(i, 0, name_item)
            self.table.setItem(i, 1, QTableWidgetItem(c['unit'] or ''))

            dir_sym = DIRECTION_SYMBOLS.get(c['direction'], '')
            dir_label = t(DIRECTION_KEYS[c['direction']]) if c['direction'] in DIRECTION_KEYS else ''
            dir_item = QTableWidgetItem(f"{dir_sym} {dir_label}")
            dir_item.setForeground(QColor(COLORS['primary']))
            self.table.setItem(i, 2, dir_item)

            self.table.setItem(i, 3, QTableWidgetItem(c['current_value'] or ''))
            self.table.setItem(i, 4, QTableWidgetItem(c['target_value'] or ''))

            diff_item = QTableWidgetItem(f"{c['difficulty']:.1f}")
            diff_item.setTextAlignment(Qt.AlignCenter)
            # Color code difficulty
            if c['difficulty'] >= 4:
                diff_item.setBackground(QColor('#FADBD8'))
            elif c['difficulty'] >= 3:
                diff_item.setBackground(QColor('#FDEBD0'))
            else:
                diff_item.setBackground(QColor('#D5F5E3'))
            self.table.setItem(i, 5, diff_item)

            self.table.setItem(i, 6, QTableWidgetItem(str(c['sort_order'])))

        self.count_label.setText(t("ctq.count", n=len(ctqs)))

    def _on_row_changed(self, row, col, prev_row, prev_col):
        if row < 0:
            return
        item = self.table.item(row, 0)
        if not item:
            return
        ctq_id = item.data(Qt.UserRole)
        ctq = self.db.conn.execute("SELECT * FROM ctq WHERE id=?", (ctq_id,)).fetchone()
        if not ctq:
            return
        self.edit_name.setText(ctq['name'])
        self.edit_unit.setText(ctq['unit'] or '')
        idx = self.edit_direction.findData(ctq['direction'])
        if idx >= 0:
            self.edit_direction.setCurrentIndex(idx)
        self.edit_target.setText(ctq['target_value'] or '')
        self.edit_current.setText(ctq['current_value'] or '')
        self.edit_difficulty.setValue(ctq['difficulty'] or 3.0)

    def _save_current(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, t("common.hint"), t("ctq.select_first"))
            return
        item = self.table.item(row, 0)
        ctq_id = item.data(Qt.UserRole)
        self.db.update_ctq(ctq_id,
            name=self.edit_name.text(),
            unit=self.edit_unit.text(),
            direction=self.edit_direction.currentData(),
            target_value=self.edit_target.text(),
            difficulty=self.edit_difficulty.value(),
        )
        # current_value goes through the sync helper so CBA's self-competitor
        # benchmark and HOQ's basement "self" row stay identical to this value.
        self.db.sync_self_ctq_score(self.project_id, ctq_id, self.edit_current.text())
        self.refresh()
        self.data_changed.emit()

    def _add_ctq(self):
        if not self.project_id:
            return
        self.db.add_ctq(self.project_id, t("ctq.new_item_name"), phase=self.phase)
        self.refresh()
        # Auto-select last row (the one just added)
        last = self.table.rowCount() - 1
        if last >= 0:
            self.table.setCurrentCell(last, 0)
            self.table.scrollToItem(self.table.item(last, 0))
        self.data_changed.emit()

    def _move_ctq(self, direction):
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 0)
        if not item:
            return
        ctq_id = item.data(Qt.UserRole)
        ctqs = self.db.get_ctqs(self.project_id, self.phase)
        ids = [c['id'] for c in ctqs]
        if ctq_id not in ids:
            return
        idx = ids.index(ctq_id)
        new_idx = idx + direction
        if 0 <= new_idx < len(ids):
            for i, cid in enumerate(ids):
                self.db.update_ctq(cid, sort_order=i)
            self.db.update_ctq(ids[idx], sort_order=new_idx)
            self.db.update_ctq(ids[new_idx], sort_order=idx)
            self.refresh()
            self.table.setCurrentCell(new_idx, 0)
            self.data_changed.emit()

    def _delete_ctq(self):
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 0)
        ctq_id = item.data(Qt.UserRole)
        reply = QMessageBox.question(self, t("msg.confirm_delete_title"),
            t("ctq.confirm_delete_body", name=item.text()),
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete_ctq(ctq_id)
            self.refresh()
            self.data_changed.emit()
