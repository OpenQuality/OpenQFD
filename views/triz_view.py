"""
TRIZ Module - Inventive Principles & Contradiction Matrix
40 Inventive Principles, 39 Engineering Parameters, Contradiction Matrix lookup.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QGroupBox, QTextBrowser,
    QHeaderView, QAbstractItemView, QSplitter, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

from utils.i18n import t, get_language

# ── 40 Inventive Principles: (cn_name, en_name, desc_zh, desc_en) ──────────
PRINCIPLES_40 = [
    ("1. 分割", "1. Segmentation", "将物体分成独立的部分；使物体成为可拆卸的；增加物体的分割程度。",
     "Divide an object into independent parts; make an object easy to disassemble; increase the degree of fragmentation."),
    ("2. 抽取", "2. Taking out", "从物体中抽取出'干扰'部分或特性；从物体中抽取出唯一需要的部分或特性。",
     "Separate an interfering part or property from an object, or single out the only necessary part (or property) of an object."),
    ("3. 局部质量", "3. Local quality", "将物体或环境的同质结构变为异质结构；让物体的不同部分各具不同功能。",
     "Change an object's structure (or its environment) from uniform to non-uniform; make each part of an object function in conditions most suitable for its operation."),
    ("4. 非对称", "4. Asymmetry", "用非对称形式取代对称形式。",
     "Replace a symmetrical form with an asymmetrical form."),
    ("5. 组合", "5. Merging", "在空间上将相同或相关的物体组合起来；在时间上将相同或相关的操作组合起来。",
     "Bring together (merge) identical or similar objects in space; bring together identical or similar operations in time."),
    ("6. 多用性", "6. Universality", "一个物体执行多种功能，去掉多余部件。",
     "Make a part or object perform multiple functions, eliminating the need for other parts."),
    ("7. 嵌套", "7. Nested doll", "将一个物体放入另一个物体中；一个物体通过另一个物体的空腔。",
     "Place one object inside another; pass one object through a cavity in the other."),
    ("8. 反重力", "8. Anti-weight", "用与其他物体相结合的方式补偿物体的重量。",
     "Compensate for an object's weight by merging it with other objects that provide lift."),
    ("9. 预先反作用", "9. Preliminary anti-action", "如果需要做某种作用，应预先实行反作用。",
     "If an action will have both useful and harmful effects, replace it with anti-actions to control the harmful effects beforehand."),
    ("10. 预先作用", "10. Preliminary action", "预先对物体进行必要的改变。",
     "Perform the required change of an object, fully or partially, before it is needed."),
    ("11. 预先防范", "11. Beforehand cushioning", "预先准备好应急措施以补偿物体相对较低的可靠性。",
     "Prepare emergency measures beforehand to compensate for an object's relatively low reliability."),
    ("12. 等势原理", "12. Equipotentiality", "改变工作条件使物体不需要升降。",
     "Change operating conditions so an object does not need to be raised or lowered."),
    ("13. 反向", "13. The other way round", "用相反的作用代替问题所要求的作用；使物体可动部分固定，固定部分可动。",
     "Invert the action used to solve the problem; make movable parts fixed and fixed parts movable."),
    ("14. 曲面化", "14. Spheroidality", "从直线运动到曲线运动；用球体代替立方体。",
     "Replace linear parts or flat surfaces with curved ones; replace cubic forms with spherical forms; use rollers or spirals."),
    ("15. 动态化", "15. Dynamics", "使物体或环境的特性自动调节到每个工作阶段的最佳状态。",
     "Allow the characteristics of an object, environment, or process to change to be optimal at each stage of operation."),
    ("16. 不足或过量", "16. Partial or excessive actions", "如果难以获得100%所需的效果，则略多或略少地实现。",
     "If 100% of an effect is hard to achieve, use \"slightly less\" or \"slightly more\" to greatly simplify the problem."),
    ("17. 维数变化", "17. Another dimension", "从一维运动变为二维或三维运动。",
     "Move an object in two or three dimensions instead of one; use a multi-story arrangement instead of a single-story one."),
    ("18. 机械振动", "18. Mechanical vibration", "使物体振动；增加振动频率直至超声波。",
     "Cause an object to oscillate or vibrate; increase its frequency, even up to the ultrasonic."),
    ("19. 周期性作用", "19. Periodic action", "用周期性作用代替连续性作用。",
     "Replace a continuous action with a periodic (pulsed) one."),
    ("20. 有效作用的连续性", "20. Continuity of useful action", "使物体的所有部分一直处于满负荷工作状态。",
     "Carry out an action continuously, so all parts of an object work at full load all the time."),
    ("21. 快速通过", "21. Skipping", "高速执行有害或危险的操作。",
     "Conduct a harmful or hazardous operation at high speed."),
    ("22. 变害为利", "22. Blessing in disguise", "利用有害因素获得有益效果。",
     "Use harmful factors (especially environmental) to achieve a positive effect."),
    ("23. 反馈", "23. Feedback", "引入反馈以改善过程或作用。",
     "Introduce feedback to improve a process or action."),
    ("24. 中间物", "24. Intermediary", "使用中间物体来传递或执行作用。",
     "Use an intermediary object to transfer or carry out an action."),
    ("25. 自服务", "25. Self-service", "使物体能够自己服务自己并执行辅助和修理操作。",
     "Make an object serve itself by performing auxiliary and repair operations."),
    ("26. 复制", "26. Copying", "用简单廉价的复制品代替昂贵的易碎物体。",
     "Replace an expensive, fragile object with simple, cheap copies."),
    ("27. 廉价替代", "27. Cheap disposables", "用廉价短寿命物体替代昂贵耐用物体。",
     "Replace an expensive, durable object with a set of cheap, short-lived objects."),
    ("28. 机械系统替代", "28. Mechanics substitution", "用光学、声学、热学等系统替代机械系统。",
     "Replace a mechanical system with an optical, acoustic, thermal, or other sensory system."),
    ("29. 气压或液压结构", "29. Pneumatics and hydraulics", "用气体或液体代替固体部件。",
     "Replace solid parts of an object with gas or liquid."),
    ("30. 柔性壳和薄膜", "30. Flexible shells and thin films", "用柔性壳和薄膜代替常规结构。",
     "Use flexible shells and thin films instead of conventional structures."),
    ("31. 多孔材料", "31. Porous materials", "使物体多孔或添加多孔元素。",
     "Make an object porous, or add porous elements."),
    ("32. 改变颜色", "32. Color changes", "改变物体或环境的颜色或透明度。",
     "Change the color or transparency of an object or its environment."),
    ("33. 同质性", "33. Homogeneity", "使与主体相互作用的物体由同一材料制成。",
     "Make objects that interact with a given object out of the same material."),
    ("34. 抛弃与恢复", "34. Discarding and recovering", "使已完成功能的物体部分消失或直接在工作中改变。",
     "Make a part of an object that has completed its function disappear or change directly during operation."),
    ("35. 参数变化", "35. Parameter changes", "改变物体的物理状态、浓度、密度、柔性、温度。",
     "Change an object's physical state, concentration, density, flexibility, or temperature."),
    ("36. 相变", "36. Phase transitions", "利用相变过程中产生的效应。",
     "Use effects that occur during phase transitions."),
    ("37. 热膨胀", "37. Thermal expansion", "利用材料的热膨胀或热收缩。",
     "Use thermal expansion or contraction of materials."),
    ("38. 加速氧化", "38. Strong oxidants", "用富氧空气代替普通空气；用纯氧代替空气。",
     "Replace normal air with oxygen-enriched air; replace enriched air with pure oxygen."),
    ("39. 惰性环境", "39. Inert atmosphere", "用惰性环境代替通常环境。",
     "Replace a normal environment with an inert one."),
    ("40. 复合材料", "40. Composite materials", "用复合材料代替均匀材料。",
     "Replace a homogeneous material with a composite material."),
]

# ── 39 Engineering Parameters: (cn, en) ─────────────────────────
PARAMS_39 = [
    ("1.运动物体的重量", "1. Weight of moving object"), ("2.静止物体的重量", "2. Weight of stationary object"),
    ("3.运动物体的长度", "3. Length of moving object"), ("4.静止物体的长度", "4. Length of stationary object"),
    ("5.运动物体的面积", "5. Area of moving object"), ("6.静止物体的面积", "6. Area of stationary object"),
    ("7.运动物体的体积", "7. Volume of moving object"), ("8.静止物体的体积", "8. Volume of stationary object"),
    ("9.速度", "9. Speed"), ("10.力", "10. Force"), ("11.张力/压力", "11. Tension/Pressure"),
    ("12.形状", "12. Shape"), ("13.结构稳定性", "13. Stability of composition"), ("14.强度", "14. Strength"),
    ("15.运动物体耐久性", "15. Durability of moving object"), ("16.静止物体耐久性", "16. Durability of stationary object"),
    ("17.温度", "17. Temperature"), ("18.亮度", "18. Illumination intensity"),
    ("19.运动物体的能量", "19. Energy spent by moving object"), ("20.静止物体的能量", "20. Energy spent by stationary object"),
    ("21.功率", "21. Power"), ("22.能量损失", "22. Loss of energy"), ("23.物质损失", "23. Loss of substance"),
    ("24.信息损失", "24. Loss of information"), ("25.时间损失", "25. Loss of time"), ("26.物质的量", "26. Quantity of substance"),
    ("27.可靠性", "27. Reliability"), ("28.测量精度", "28. Measurement accuracy"), ("29.制造精度", "29. Manufacturing precision"),
    ("30.物体上有害因素", "30. Harmful factors acting on object"), ("31.有害副作用", "31. Harmful side effects"),
    ("32.可制造性", "32. Manufacturability"), ("33.使用方便性", "33. Ease of use"), ("34.可维修性", "34. Ease of repair"),
    ("35.适应性", "35. Adaptability"), ("36.装置复杂性", "36. Device complexity"), ("37.控制复杂性", "37. Control complexity"),
    ("38.自动化程度", "38. Degree of automation"), ("39.生产率", "39. Productivity"),
]

# Simplified contradiction matrix (most common entries)
# Full 39x39 matrix - using most referenced principle suggestions
# Format: MATRIX[improving][worsening] = [principle_numbers]
# This is a representative subset; full matrix has 1263 cells
_SAMPLE_MATRIX = {
    (0,1): [2,26,29,40], (0,2): [15,8,29,34], (0,8): [2,28,13,38],
    (0,13): [29,17,38,34], (0,38): [35,26,24,37], (1,0): [10,1,29,35],
    (1,12): [13,29,10,18], (1,25): [36,22], (2,8): [15,17,4],
    (3,12): [1,8,15,34], (4,13): [30,2,14,18], (5,13): [26,7,9,39],
    (8,9): [13,28,15,12], (8,12): [35,15,34,18], (8,38): [28,15,10,36],
    (9,10): [36,35,21], (9,13): [10,36,37,40], (10,12): [35,4,15,10],
    (11,12): [15,14,28,26], (12,10): [21,35,2,39], (12,13): [13,4,1],
    (13,8): [3,35,10,40], (13,12): [11,28,1,4], (13,38): [35,28,2,24],
    (14,15): [19,5,34,31], (16,13): [36,22,6,38], (16,18): [19,38,7],
    (20,21): [19,24,3,14], (21,22): [7,2,6,13], (22,24): [28,27,18,38],
    (25,26): [6,3,10,24], (26,30): [27,40,28,8], (27,28): [32,26,28,18],
    (28,26): [28,32,1,24], (30,31): [22,35,18,39], (31,30): [19,22,15,39],
    (32,33): [27,26,1,13], (33,34): [1,13,2,4], (34,35): [15,34,1,16],
    (35,36): [15,29,37,28], (36,37): [28,26,18,35], (37,38): [28,26,35,10],
    (38,25): [35,26,10,28], (38,30): [35,22,18,39],
}


def _param_name(idx):
    cn, en = PARAMS_39[idx]
    return cn if get_language() == "zh_CN" else en


def _principle_name(idx):
    cn, en, desc_zh, desc_en = PRINCIPLES_40[idx]
    return cn if get_language() == "zh_CN" else en


def _principle_desc(idx):
    cn, en, desc_zh, desc_en = PRINCIPLES_40[idx]
    return desc_zh if get_language() == "zh_CN" else desc_en


class TRIZView(QWidget):
    """TRIZ Inventive Principles browser and Contradiction Matrix lookup."""
    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        lbl = QLabel(t("triz.title"))
        lbl.setObjectName("title")
        layout.addWidget(lbl)

        self.tabs = __import__('PySide6.QtWidgets', fromlist=['QTabWidget']).QTabWidget()

        # Tab 1: Contradiction Matrix
        matrix_tab = QWidget()
        self._setup_matrix_tab(matrix_tab)
        self.tabs.addTab(matrix_tab, t("triz.tab_matrix"))

        # Tab 2: 40 Principles browser
        principles_tab = QWidget()
        self._setup_principles_tab(principles_tab)
        self.tabs.addTab(principles_tab, t("triz.tab_principles"))

        layout.addWidget(self.tabs)

    def _setup_matrix_tab(self, parent):
        layout = QVBoxLayout(parent)
        hint = QLabel(t("triz.matrix_hint"))
        hint.setObjectName("subtitle")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        form = QHBoxLayout()
        form.addWidget(QLabel(t("triz.improving_param")))
        self.improving_combo = QComboBox()
        self.improving_combo.addItems([_param_name(i) for i in range(len(PARAMS_39))])
        self.improving_combo.setMinimumWidth(250)
        form.addWidget(self.improving_combo)

        form.addWidget(QLabel(t("triz.worsening_param")))
        self.worsening_combo = QComboBox()
        self.worsening_combo.addItems([_param_name(i) for i in range(len(PARAMS_39))])
        self.worsening_combo.setMinimumWidth(250)
        form.addWidget(self.worsening_combo)

        btn = QPushButton(t("triz.lookup"))
        btn.clicked.connect(self._lookup_principles)
        form.addWidget(btn)
        form.addStretch()
        layout.addLayout(form)

        self.result_browser = QTextBrowser()
        self.result_browser.setStyleSheet("font-size: 14px; padding: 12px; background: white;")
        layout.addWidget(self.result_browser)

    def _setup_principles_tab(self, parent):
        layout = QHBoxLayout(parent)
        splitter = QSplitter(Qt.Horizontal)

        self.principle_list = QListWidget()
        self.principle_list.setMaximumWidth(300)
        for idx in range(len(PRINCIPLES_40)):
            item = QListWidgetItem(_principle_name(idx))
            item.setData(Qt.UserRole, idx)
            self.principle_list.addItem(item)
        self.principle_list.currentRowChanged.connect(self._on_principle_selected)
        splitter.addWidget(self.principle_list)

        self.principle_detail = QTextBrowser()
        self.principle_detail.setStyleSheet("font-size: 14px; padding: 16px;")
        splitter.addWidget(self.principle_detail)
        splitter.setSizes([300, 600])
        layout.addWidget(splitter)

    def _lookup_principles(self):
        i = self.improving_combo.currentIndex()
        w = self.worsening_combo.currentIndex()
        if i == w:
            self.result_browser.setHtml(f"<p style='color:#E74C3C;'>{t('triz.same_param_error')}</p>")
            return
        principles = _SAMPLE_MATRIX.get((i, w), [])
        if not principles:
            # Try reverse
            principles = _SAMPLE_MATRIX.get((w, i), [])
        if principles:
            html = f"<h3>{t('triz.result_header', improving=_param_name(i), worsening=_param_name(w))}</h3>"
            html += f"<p>{t('triz.recommended')}</p><ul>"
            for pn in principles:
                if 1 <= pn <= 40:
                    idx = pn - 1
                    html += f"<li><b>{_principle_name(idx)}</b><br/><span style='color:#555;'>{_principle_desc(idx)}</span></li>"
            html += "</ul>"
        else:
            html = f"<p>{t('triz.no_recommendation')}</p>"
        self.result_browser.setHtml(html)

    def _on_principle_selected(self, row):
        if 0 <= row < len(PRINCIPLES_40):
            self.principle_detail.setHtml(
                f"<h2>{_principle_name(row)}</h2>"
                f"<p style='font-size:15px; line-height:1.8;'>{_principle_desc(row)}</p>")
