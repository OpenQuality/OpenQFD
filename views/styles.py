"""
QFD Application - Shared Styles & Constants
"""

COLORS = {
    'primary': '#1B5E8C',
    'primary_light': '#2980B9',
    'primary_dark': '#154A70',
    'accent': '#E67E22',
    'success': '#27AE60',
    'danger': '#E74C3C',
    'warning': '#F39C12',
    'bg': '#F5F7FA',
    'bg_dark': '#E8ECF1',
    'card': '#FFFFFF',
    'text': '#2C3E50',
    'text_light': '#7F8C8D',
    'border': '#D5DBE1',
    'hover': '#EBF5FB',
    'selected': '#D4E6F1',
    'roof_strong_pos': '#1B7A1B',
    'roof_pos': '#7BC67B',
    'roof_neg': '#E88E8E',
    'roof_strong_neg': '#C0392B',
    'rel_strong': '#1B5E8C',
    'rel_medium': '#5DADE2',
    'rel_weak': '#AED6F1',
}

PHASE_NAMES = {
    1: "阶段一：产品规划",
    2: "阶段二：零件展开",
    3: "阶段三：工艺规划",
    4: "阶段四：生产控制",
}

PHASE_ROW_LABELS = {
    1: "顾客需求 (VOC)",
    2: "质量特性（CTQ）",
    3: "零件特性",
    4: "工艺参数",
}

PHASE_COL_LABELS = {
    1: "质量特性（CTQ）",
    2: "零件特性",
    3: "工艺参数",
    4: "生产控制措施",
}

DIRECTION_LABELS = {
    'higher_better': '↑ 越大越好',
    'lower_better': '↓ 越小越好',
    'target': '◎ 目标值型',
}
# Maps each DIRECTION_LABELS code to its i18n key
DIRECTION_KEYS = {
    'higher_better': 'dir.higher', 'lower_better': 'dir.lower', 'target': 'dir.target',
}

DIRECTION_SYMBOLS = {
    'higher_better': '▲',
    'lower_better': '▼',
    'target': '◎',
}

KANO_TYPES = {
    'M': '基本型 (Must-be)',
    'O': '期望型 (One-dimensional)',
    'A': '魅力型 (Attractive)',
    'I': '无差异型 (Indifferent)',
    'R': '逆向型 (Reverse)',
    '': '未分类',
}
# Maps each KANO_TYPES code to its i18n key
KANO_TYPE_KEYS = {
    'M': 'kano.must_be', 'O': 'kano.one_dim', 'A': 'kano.attractive',
    'I': 'kano.indifferent', 'R': 'kano.reverse', '': 'kano.unclassified',
}

INDUSTRIES = [
    "汽车制造", "消费电子", "软件开发", "医疗器械",
    "服务业", "航空航天", "食品饮料", "通用制造", "其他"
]
# Maps each INDUSTRIES entry (the canonical value stored in the DB) to its i18n key
INDUSTRY_KEYS = [
    "ind.auto", "ind.electronics", "ind.software", "ind.medical",
    "ind.service", "ind.aerospace", "ind.food", "ind.general", "ind.other",
]

_MAIN_STYLESHEET_TEMPLATE = """
QMainWindow {
    background-color: #F5F7FA;
}
QWidget {
    font-family: "Microsoft YaHei", "Segoe UI", "PingFang SC", sans-serif;
    font-size: 13px;
    line-height: 1.2;
    color: #2C3E50;
}
QLabel#title {
    font-size: 18px;
    font-weight: bold;
    color: #1B5E8C;
}
QLabel#subtitle {
    font-size: 14px;
    color: #7F8C8D;
}
QPushButton {
    background-color: #1B5E8C;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 13px;
    line-height: 1.2;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #2980B9;
}
QPushButton:pressed {
    background-color: #0D3B5E;
}
QPushButton:disabled {
    background-color: #BDC3C7;
}
QPushButton#secondary {
    background-color: transparent;
    color: #1B5E8C;
    border: 1.5px solid #1B5E8C;
}
QPushButton#secondary:hover {
    background-color: #EBF5FB;
}
QPushButton#danger {
    background-color: #E74C3C;
}
QPushButton#danger:hover {
    background-color: #C0392B;
}
QPushButton#success {
    background-color: #27AE60;
}
QPushButton#accent {
    background-color: #E67E22;
}
QPushButton#accent:hover {
    background-color: #D35400;
}
QPushButton#flat {
    background-color: transparent;
    color: #1B5E8C;
    border: none;
    padding: 4px 8px;
}
QPushButton#flat:hover {
    background-color: #EBF5FB;
    border-radius: 4px;
}
QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    border: 1.5px solid #D5DBE1;
    border-radius: 6px;
    padding: 7px 10px;
    background-color: white;
    color: #2C3E50;
    selection-background-color: #D4E6F1;
    selection-color: #1B5E8C;
}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border-color: #2980B9;
}
QComboBox::drop-down {
    border: none;
    border-left: 1.5px solid #D5DBE1;
    width: 26px;
    background-color: #EBF5FB;
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
}
QComboBox::drop-down:hover {
    background-color: #D4E6F1;
}
QComboBox::down-arrow {
    image: url(__ARROW_DOWN__);
    width: 11px;
    height: 11px;
}
QComboBox::down-arrow:disabled {
    image: url(__ARROW_DOWN_DISABLED__);
}
QComboBox QAbstractItemView {
    background-color: white;
    color: #2C3E50;
    selection-background-color: #D4E6F1;
    selection-color: #1B5E8C;
    outline: none;
}
QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 20px;
    height: 14px;
    border-left: 1.5px solid #D5DBE1;
    border-bottom: 1px solid #D5DBE1;
    border-top-right-radius: 5px;
    background-color: #EBF5FB;
}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
    background-color: #D4E6F1;
}
QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 20px;
    height: 14px;
    border-left: 1.5px solid #D5DBE1;
    border-bottom-right-radius: 5px;
    background-color: #EBF5FB;
}
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #D4E6F1;
}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    image: url(__ARROW_UP__);
    width: 9px;
    height: 9px;
}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    image: url(__ARROW_DOWN__);
    width: 9px;
    height: 9px;
}
QSpinBox::up-arrow:disabled, QSpinBox::up-arrow:off,
QDoubleSpinBox::up-arrow:disabled, QDoubleSpinBox::up-arrow:off {
    image: url(__ARROW_UP_DISABLED__);
}
QSpinBox::down-arrow:disabled, QSpinBox::down-arrow:off,
QDoubleSpinBox::down-arrow:disabled, QDoubleSpinBox::down-arrow:off {
    image: url(__ARROW_DOWN_DISABLED__);
}
QTableWidget {
    gridline-color: #D5DBE1;
    background-color: white;
    alternate-background-color: #F8F9FA;
    selection-background-color: transparent;
    selection-color: #E74C3C;
    border: 1px solid #D5DBE1;
    border-radius: 6px;
}
QTableWidget::item {
    padding: 0px 4px;
    font-size: 13px;
}
QTableWidget::item:selected {
    background: transparent;
    color: #E74C3C;
}
QTableWidget QLineEdit {
    background: white;
    color: #333;
    font-size: 13px;
    border: 2px solid #1565C0;
    padding: 0px 3px;
}
QHeaderView::section {
    background-color: #EBF5FB;
    color: #1B5E8C;
    font-weight: bold;
    border: 1px solid #D5DBE1;
    padding: 8px 6px;
}
QTreeWidget {
    border: 1px solid #D5DBE1;
    border-radius: 6px;
    background-color: white;
    alternate-background-color: #F8F9FA;
}
QTreeWidget::item {
    padding: 6px 5px;
    border-bottom: 1px solid #EEF0F2;
    font-size: 13px;
    line-height: 1.2;
}
QTreeWidget::item:selected {
    background-color: #D4E6F1;
    color: #1B5E8C;
}
QScrollBar:vertical {
    background: #F0F0F0;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #BDC3C7;
    min-height: 30px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #95A5A6;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: #F0F0F0;
    height: 10px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background: #BDC3C7;
    min-width: 30px;
    border-radius: 5px;
}
QTabWidget::pane {
    border: 1px solid #D5DBE1;
    border-radius: 6px;
    background-color: white;
}
QTabBar::tab {
    background-color: #EBF5FB;
    color: #2C3E50;
    border: 1px solid #D5DBE1;
    border-bottom: none;
    padding: 8px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}
QTabBar::tab:selected {
    background-color: white;
    color: #1B5E8C;
    font-weight: bold;
}
QGroupBox {
    font-weight: bold;
    border: 1.5px solid #D5DBE1;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
    color: #1B5E8C;
}
QToolTip {
    background-color: #2C3E50;
    color: white;
    border: none;
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 12px;
}
QSplitter::handle {
    background-color: #D5DBE1;
}
QSplitter::handle:horizontal {
    width: 2px;
}
QMessageBox {
    background-color: white;
}
"""


def build_main_stylesheet(assets_dir):
    """Fill in the combobox/spinbox arrow icon paths (must be forward-slashed
    absolute paths for Qt's stylesheet url() regardless of OS) and return the
    complete application stylesheet."""
    import os as _os
    def _url(name):
        return _os.path.join(assets_dir, name).replace("\\", "/")
    return (_MAIN_STYLESHEET_TEMPLATE
            .replace("__ARROW_DOWN__", _url("arrow_down.png"))
            .replace("__ARROW_UP__", _url("arrow_up.png"))
            .replace("__ARROW_DOWN_DISABLED__", _url("arrow_down_disabled.png"))
            .replace("__ARROW_UP_DISABLED__", _url("arrow_up_disabled.png")))


SIDEBAR_STYLE = """
QListWidget {
    background-color: #154A70;
    border: none;
    outline: none;
    font-size: 13px;
    line-height: 1.2;
    padding: 4px;
}
QListWidget::item {
    color: #AED6F1;
    padding: 9px 14px;
    border-radius: 8px;
    margin: 1px 6px;
}
QListWidget::item:hover {
    background-color: #1B5E8C;
    color: white;
}
QListWidget::item:selected {
    background-color: #2980B9;
    color: white;
    font-weight: bold;
}
"""
