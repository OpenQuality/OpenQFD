"""
OpenQFD Help Manual - Comprehensive in-app documentation
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser,
    QPushButton, QListWidget, QListWidgetItem, QSplitter, QLabel
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from utils.i18n import t, get_language
from models.license import APP_VERSION

HELP_SECTIONS = {
"zh_CN": [

# ─── 1. 快速入门 ───
("快速入门", """<h2>快速入门指南</h2>
<p>OpenQFD 是一款专业的质量功能展开(QFD)分析软件，帮助您将客户需求系统地转化为产品技术参数。</p>

<h3>软件启动</h3>
<p>双击启动后，您会看到项目列表界面。有三种方式开始使用：</p>
<ul>
<li><b>📁 创建新项目</b> — 从零开始，输入项目名称、行业、评分量表</li>
<li><b>📋 加载示例项目</b> — 载入"智能手表QFD"示例数据，立即体验完整功能</li>
<li><b>📥 导入JSON项目</b> — 导入之前导出的项目备份文件</li>
</ul>
<p style="color:#1565C0;"><b>💡 建议：第一次使用请点击「加载示例项目」，先熟悉软件功能，再创建自己的项目。</b></p>

<h3>界面结构</h3>
<p>打开项目后，界面分为两部分：</p>
<ul>
<li><b>左侧导航栏</b> — 各功能模块入口（VOC、CTQ、质量屋、分析工具等）</li>
<li><b>右侧工作区</b> — 当前模块的操作界面</li>
</ul>
<p>顶部菜单栏可进行项目管理（新建/打开/加载示例/导入/删除），以及「授权」「帮助」菜单中的授权管理、帮助手册、语言切换。</p>
<p>带 🔒 标记的模块为授权版功能，需要激活授权码才能使用。</p>

<h3>核心工作流程</h3>
<p>构建一个完整的质量屋(HOQ)，需要按以下顺序操作：</p>
<ol>
<li>录入顾客需求 (VOC) — <i>客户想要什么？</i></li>
<li>录入质量特性（CTQ）— <i>产品怎样实现？</i></li>
<li>添加竞争对手 — <i>对手表现如何？</i></li>
<li>填写关系矩阵 — <i>VOC和CTQ之间的关联强度</i></li>
<li>填写屋顶相关矩阵 — <i>CTQ之间的相互影响</i></li>
<li>查看分析结果 — <i>哪些技术参数最重要？</i></li>
</ol>
<p><b>详细步骤请查看「构建质量屋」章节。</b></p>"""),

# ─── 2. 构建质量屋（核心教程）───
("构建质量屋", """<h2>手把手：构建一个完整的质量屋</h2>
<p>以下以"智能手表"为例，带您完成一个完整的 HOQ 分析。</p>

<hr/>
<h3>第一步：录入顾客需求 (VOC)</h3>
<p>在左侧导航点击 <b>📋 顾客需求(VOC)</b> 进入。</p>

<p><b>操作方法：</b></p>
<ol>
<li>点击 <b>「+ 添加需求」</b></li>
<li>在右侧详情面板中填写：
  <ul>
  <li><b>名称</b>：如"电池续航长"、"屏幕清晰"、"佩戴舒适"等</li>
  <li><b>客户重要度</b>：1-5分（5=最重要）</li>
  <li><b>来源</b>：市场调研 / 客户访谈 / 投诉反馈 等</li>
  <li><b>Kano分类</b>：基本型(M) / 期望型(O) / 魅力型(A) 等</li>
  </ul>
</li>
<li>点击 <b>「💾 保存修改」</b></li>
<li>重复以上步骤，添加所有顾客需求（建议5-15条）</li>
</ol>

<p><b>高级功能：</b></p>
<ul>
<li><b>树状嵌套</b>：选中一条需求后点击「+ 添加子需求」，可创建需求层级（如"外观→颜色、形状、材质"）</li>
<li><b>批量导入</b>：点击「📥 批量导入」，从 Excel/CSV 文件导入</li>
<li><b>搜索过滤</b>：用搜索框和Kano类型过滤器快速定位</li>
</ul>

<p style="background:#FFF3E0; padding:10px; border-radius:6px;">
<b>💡 提示：</b>每条VOC的「客户重要度」必须填写，否则质量屋中该行的权重计算结果为0。建议每条都认真评分。
</p>

<hr/>
<h3>第二步：录入质量特性（CTQ）</h3>
<p>点击 <b>🔧 质量特性（CTQ）</b> 进入。</p>

<p><b>操作方法：</b></p>
<ol>
<li>点击 <b>「+ 添加CTQ」</b></li>
<li>在右侧填写：
  <ul>
  <li><b>名称</b>：如"电池容量"、"屏幕分辨率"、"整机重量"</li>
  <li><b>单位</b>：mAh、PPI、g 等</li>
  <li><b>优化方向</b>：
    <ul>
    <li>↑ 越大越好（如电池容量）</li>
    <li>↓ 越小越好（如整机重量）</li>
    <li>◎ 目标值型（如防水等级）</li>
    </ul>
  </li>
  <li><b>目标值</b>：产品设计的目标数值</li>
  <li><b>技术难度</b>：1-5分</li>
  </ul>
</li>
<li>点击 <b>「💾 保存修改」</b></li>
</ol>

<p style="background:#FFF3E0; padding:10px; border-radius:6px;">
<b>💡 提示：</b>CTQ 的「单位」和「优化方向」会显示在质量屋的列头（天花板），帮助阅读者理解每个技术参数的含义。
</p>

<hr/>
<h3>第三步：添加竞争对手</h3>
<p>点击 <b>🏢 竞争基准分析</b> 进入。</p>

<p><b>为什么需要这一步？</b>质量屋的右墙（Ui/Ti/Ri/Wi列）和地下室（竞品技术基准）都依赖竞品数据。<b>不添加竞争对手，右墙和地下室会是空的。</b></p>

<p><b>操作方法：</b></p>
<ol>
<li>在「竞争对手管理」中点击 <b>「+ 添加竞争对手」</b></li>
<li>添加 2-4 个竞争对手，例如：
  <ul>
  <li>我方产品（勾选"是否自身"复选框）</li>
  <li>竞品A（如 Apple Watch）</li>
  <li>竞品B（如 Galaxy Watch）</li>
  </ul>
</li>
<li><b>填写VOC满意度评分</b>：在「VOC评分矩阵」标签页中，为每个竞品的每条VOC打分（1-5分）
  <ul>
  <li>「我方产品」的VOC评分 → 对应质量屋右墙的 <b>Ui（当前水平）</b></li>
  </ul>
</li>
<li><b>填写CTQ评分基准</b>：在「CTQ评分基准」标签页中，填入各竞品的技术参数实际值
  <ul>
  <li>如 Apple Watch 的电池容量 = 430 mAh</li>
  <li>这些数据 → 显示在质量屋的 <b>地下室</b></li>
  </ul>
</li>
</ol>

<p style="background:#E8F5E9; padding:10px; border-radius:6px;">
<b>✅ 完成这一步后：</b>质量屋的右墙会显示「我方」的满意度(Ui)，右侧会出现各竞品的对比列；地下室会显示各竞品的技术参数基准值。
</p>

<hr/>
<h3>第四步：填写质量屋关系矩阵</h3>
<p>点击 <b>📊 质量屋(HOQ)</b> 进入。此时质量屋应该已经显示了VOC行和CTQ列。</p>

<p><b>操作方法：</b></p>
<ol>
<li>找到中央矩阵区域（VOC行 × CTQ列的交叉格子）</li>
<li><b>单击</b>某个格子，设置该VOC与该CTQ之间的关系强度：
  <ul>
  <li>第1次点击 → <span style="color:gray;">△ 弱相关(1)</span></li>
  <li>第2次点击 → <span style="color:blue;">◎ 中相关(3)</span></li>
  <li>第3次点击 → <span style="color:red;">● 强相关(9)</span></li>
  <li>第4次点击 → 清空</li>
  </ul>
</li>
<li>逐个格子填写，<b>不是每个格子都需要填</b>——只填有关联的</li>
<li>填写完成后，底部（地板）会自动显示各CTQ的 <b>绝对权重Tai</b> 和 <b>相对权重Ti</b></li>
</ol>

<p><b>关系强度选择指南：</b></p>
<table border="1" cellpadding="5" style="border-collapse:collapse; width:100%;">
<tr style="background:#eee;"><th>强度</th><th>含义</th><th>示例</th></tr>
<tr><td style="color:red;font-size:16px;">●(9)</td><td>强相关：该CTQ直接决定此VOC能否满足</td><td>"电池容量" 强相关 "续航长"</td></tr>
<tr><td style="color:blue;font-size:16px;">◎(3)</td><td>中相关：有明显影响但非决定性</td><td>"屏幕分辨率" 中相关 "外观时尚"</td></tr>
<tr><td style="color:gray;font-size:16px;">△(1)</td><td>弱相关：有一定间接影响</td><td>"充电功率" 弱相关 "操作简便"</td></tr>
<tr><td>空</td><td>无关：二者之间没有明显关联</td><td>"电池容量" 无关 "外观时尚"</td></tr>
</table>

<p style="background:#FFF3E0; padding:10px; border-radius:6px;">
<b>💡 提示：</b>典型的 8×8 矩阵中，通常只有30-50%的格子有值（即20-30个关系）。<b>不需要每个格子都填</b>。
</p>

<hr/>
<h3>第五步：设置计划水平 (Ti)</h3>
<p>在质量屋的右墙区域，<b>Ti(计划)列</b>是黄色背景的可编辑列。</p>

<p><b>操作方法：</b></p>
<ol>
<li>双击 Ti 列的某个格子</li>
<li>输入计划达到的满意度水平（与Ui同一量纲，通常1-5分）</li>
<li>按回车或点击其他地方保存</li>
</ol>
<p>设置Ti后，系统自动计算：</p>
<ul>
<li><b>Ri = Ti / Ui</b>（改进比：计划 ÷ 当前。Ri>1表示需要改进）</li>
<li><b>Wai = Ri × Si × Ii</b>（调整权重：综合了改进幅度、销售点、重要度）</li>
<li><b>Wi</b></td><td>归一化权重：Wai占总Wai的比例）</li>
</ul>

<hr/>
<h3>第六步：填写屋顶相关矩阵</h3>
<p>质量屋上方的三角形区域（屋顶）用于标记 CTQ 之间的相互关系。</p>

<p><b>操作方法：</b></p>
<ol>
<li>点击屋顶区域的菱形格子</li>
<li>每次点击循环切换：空 → <span style="color:green;">+(正相关)</span> → <span style="color:green;">++(强正相关)</span> → <span style="color:red;">-(负相关)</span> → <span style="color:red;">--(强负相关)</span> → 空</li>
</ol>
<p>示例：</p>
<ul>
<li>"电池容量"与"整机重量"：<span style="color:red;"><b>--</b></span>（电池越大越重，强负相关）</li>
<li>"屏幕尺寸"与"屏幕分辨率"：<span style="color:green;"><b>+</b></span>（通常大屏配高分辨率）</li>
</ul>

<p style="background:#E3F2FD; padding:10px; border-radius:6px;">
<b>📊 恭喜！</b>完成以上六步后，您已经拥有一个完整的质量屋(HOQ)，包含：屋顶、天花板、左墙、房间、右墙、地板、地下室 全部七个区域的数据。
</p>

<hr/>
<h3>最终结果解读</h3>
<ul>
<li><b>地板 — 绝对权重 Tai</b>：Σ(rij × Ii)，每个CTQ的综合重要度分数</li>
<li><b>地板 — 相对权重 Ti</b>：Tai / ΣTai，归一化后的比例值</li>
<li><b>右墙 — Ri(改进比)</b>：Ti / Ui，>1 表示需要改进</li>
<li><b>右墙 — Wi(归一化权重)</b>：Wai / ΣWai，综合考虑改进空间和销售价值</li>
<li><b>M</b>：客户满意度指数（原CSI）= Σ(Ii×满意度) / (ΣIi×满分)，范围 0~1</li>
<li><b>T</b>：技术竞争力指数（原TCI）= Σ(Tai×标准化基准) / ΣTai，范围 0~1</li>
<li><b>竞品对比列</b>：快速比较各竞品在每条VOC上的满意度</li>
<li><b>地下室 — 竞品CTQ基准</b>：了解各竞品的技术参数实际值</li>
</ul>
"""),

# ─── 3. 质量屋说明 ───
("质量屋说明", """<h2>质量屋 (House of Quality) 结构</h2>

<h3>七区一体化视图</h3>
<table border="1" cellpadding="6" style="border-collapse:collapse; width:100%;">
<tr style="background:#1565C0;color:white;"><th>区域</th><th>位置</th><th>内容</th><th>数据来源</th></tr>
<tr><td><b>屋顶</b></td><td>上方三角区</td><td>CTQ间相关性 (++/+/-/--)</td><td>在HOQ中手动点击菱形格</td></tr>
<tr><td><b>天花板</b></td><td>列头</td><td>CTQ名称、单位、方向箭头</td><td>自动读取CTQ模块数据</td></tr>
<tr><td><b>左墙</b></td><td>前两列</td><td>VOC名称 + 重要度权重Ii</td><td>自动读取VOC模块数据</td></tr>
<tr><td><b>房间</b></td><td>中央矩阵</td><td>VOC-CTQ关系 (●9/◎3/△1)</td><td>在HOQ中手动点击格子</td></tr>
<tr><td><b>右墙</b></td><td>右侧多列</td><td>Ui/Ti/Ri/Si/Wai/Wi + 竞品满意度</td><td>竞品模块 + HOQ手动编辑Ti</td></tr>
<tr><td><b>地板</b></td><td>底部2行</td><td>CTQ绝对/相对权重</td><td>自动计算</td></tr>
<tr><td><b>地下室</b></td><td>最底部</td><td>竞品CTQ技术基准值</td><td>竞品模块CTQ基准矩阵</td></tr>
</table>

<h3>右墙各列说明</h3>
<table border="1" cellpadding="5" style="border-collapse:collapse; width:100%;">
<tr style="background:#eee;"><th>列名</th><th>含义</th><th>数据来源</th><th>计算公式</th></tr>
<tr><td><b>Ui</b></td><td>当前满意水平</td><td>竞品模块→「我方」VOC评分</td><td>—</td></tr>
<tr><td><b>Ti</b> ⚡</td><td>计划满意水平</td><td><b>在HOQ中手动编辑</b>（黄色格）</td><td>—</td></tr>
<tr><td><b>Ri</b></td><td>改进比</td><td>自动计算</td><td>Ti ÷ Ui</td></tr>
<tr><td><b>Si</b></td><td>销售点</td><td>VOC模块→销售点设置</td><td>—</td></tr>
<tr><td><b>Wai</b></td><td>调整后权重</td><td>自动计算</td><td>Ri × Si × Ii</td></tr>
<tr><td><b>Wi</b></td><td>归一化权重</td><td>自动计算</td><td>Wai ÷ ΣWai</td></tr>
<tr><td><b>★我方</b></td><td>我方VOC满意度</td><td>竞品模块→VOC评分</td><td>—</td></tr>
<tr><td><b>竞品A</b></td><td>竞品A满意度</td><td>竞品模块→VOC评分</td><td>—</td></tr>
</table>

<h3>常见问题：为什么右墙/地下室是空的？</h3>
<ol>
<li><b>Ui列为空</b> → 没有添加竞争对手，或没有标记「是否自身」</li>
<li><b>Ti列为空</b> → 需要双击黄色格子手动输入计划满意度</li>
<li><b>竞品列为空</b> → 没有在竞品模块填写VOC评分</li>
<li><b>地下室为空</b> → 没有在竞品模块填写CTQ基准值</li>
</ol>
"""),

# ─── 4. VOC 管理 ───
("VOC 管理", """<h2>顾客需求 (VOC) 管理</h2>
<h3>录入方式</h3>
<ul>
<li><b>手动添加</b>：逐条添加，每条可设描述、来源、Kano类型</li>
<li><b>批量导入</b>：支持 CSV/Excel，需包含"名称"或"name"列</li>
</ul>
<h3>树状结构</h3>
<p>支持最多三级嵌套。用途：用亲和图(KJ法)对需求分组。</p>
<p>示例：外观设计 → (颜色选择、材质手感、尺寸大小)</p>
<h3>重要字段说明</h3>
<table border="1" cellpadding="4" style="border-collapse:collapse; width:100%;">
<tr style="background:#eee;"><th>字段</th><th>作用</th><th>影响</th></tr>
<tr><td><b>客户重要度 Ii</b></td><td>该需求对客户有多重要</td><td>直接影响HOQ权重计算</td></tr>
<tr><td><b>计划水平</b></td><td>我方计划达到的满意度</td><td>影响HOQ右墙Ti/Ri</td></tr>
<tr><td><b>销售点 Si</b></td><td>是否作为卖点宣传</td><td>1.0(普通)/1.2(卖点)/1.5(强卖点)</td></tr>
<tr><td><b>Kano分类</b></td><td>需求属于哪种类型</td><td>影响Kano分析图表</td></tr>
</table>
<h3>Kano 分类</h3>
<table border="1" cellpadding="4" style="border-collapse:collapse;">
<tr style="background:#eee;"><th>类型</th><th>说明</th><th>策略</th></tr>
<tr><td style="color:red;"><b>基本型(M)</b></td><td>必须满足，没有就不满</td><td>优先保障</td></tr>
<tr><td style="color:blue;"><b>期望型(O)</b></td><td>满足程度越高越满意</td><td>持续改进</td></tr>
<tr><td style="color:green;"><b>魅力型(A)</b></td><td>有则惊喜，无也不失望</td><td>差异化竞争</td></tr>
<tr><td style="color:gray;">无差异(I)</td><td>有没有都无所谓</td><td>可降低投入</td></tr>
<tr><td style="color:orange;">逆向型(R)</td><td>有了反而不满</td><td>避免过度设计</td></tr>
</table>
"""),

# ─── 5. 高级分析 ───
("高级分析工具", """<h2>高级分析工具（授权版）</h2>

<h3>AHP 层次分析法</h3>
<p>通过两两比较的方式精确计算 VOC 的相对权重。</p>
<ol>
<li>进入 AHP 模块 → 自动生成 N×N 成对比较矩阵</li>
<li>填写：与行需求相比，列需求的相对重要程度（1-9标度）</li>
<li>点击「🔄 计算权重」→ 显示计算结果和一致性检验</li>
<li>CR < 0.1 为通过，点击「✅ 应用到HOQ」覆盖原有权重</li>
</ol>
<p>标度说明：1=同等重要，3=稍重要，5=明显重要，7=强烈重要，9=极端重要</p>

<h3>竞争基准分析</h3>
<p>对比我方与竞品在 VOC 和 CTQ 维度的表现。</p>
<ul>
<li><b>雷达图</b>：各竞品在每条VOC上的满意度对比</li>
<li><b>柱状图</b>：按CTQ维度对比各竞品的技术参数</li>
</ul>

<h3>Pareto 优先级分析</h3>
<p>基于HOQ计算的CTQ权重，生成帕累托图（柱状+累计曲线），快速识别占比80%的关键少数技术参数。</p>

<h3>四阶段展开</h3>
<p>ASI 模型的四阶段级联：</p>
<ol>
<li>VOC → CTQ（产品规划 — 本软件核心）</li>
<li>CTQ → 零件特性（零件展开）</li>
<li>零件特性 → 工艺参数（工艺规划）</li>
<li>工艺参数 → 生产控制措施（生产控制）</li>
</ol>
<p>每个阶段的输出(HOW)成为下一阶段的输入(WHAT)，实现需求从客户到车间的逐级传递。</p>
"""),

# ─── 6. TRIZ ───
("TRIZ 发明原理", """<h2>TRIZ 发明问题解决理论</h2>
<p>TRIZ 是前苏联发明家阿奇舒勒从250万份专利中总结的系统化创新方法论。</p>

<h3>40条发明原理</h3>
<p>切换到「💡 40条发明原理」标签页，浏览完整的40条原理（中英双语），包含原理说明。</p>
<p>常用原理举例：</p>
<ul>
<li><b>原理1：分割</b> — 将物体分成独立部分（如模块化设计）</li>
<li><b>原理5：组合</b> — 将相关操作合并（如多功能手表）</li>
<li><b>原理13：反向</b> — 用相反方式思考问题</li>
<li><b>原理15：动态化</b> — 让特性自动适应环境</li>
<li><b>原理35：参数变化</b> — 改变物理状态解决问题</li>
</ul>

<h3>矛盾矩阵</h3>
<p>当改善一个参数会导致另一个参数恶化时，使用矛盾矩阵查找推荐的发明原理。</p>
<p><b>操作步骤：</b></p>
<ol>
<li>进入 TRIZ → 矛盾矩阵 标签页</li>
<li>在第一个下拉框选择「要改善的参数」（如"速度"）</li>
<li>在第二个下拉框选择「会恶化的参数」（如"运动物体的重量"）</li>
<li>点击「🔍 查找原理」</li>
<li>系统自动推荐2-4条发明原理，含详细说明</li>
</ol>

<h3>39个工程参数</h3>
<p>涵盖：运动/静止物体的重量、长度、面积、体积，速度、力、张力、形状、结构稳定性、强度、耐久性、温度、亮度、能量、功率、能量损失、物质损失、信息损失、时间损失、可靠性、精度、复杂性、自动化程度、生产率等。</p>
"""),

# ─── 7. FMEA ───
("FMEA 失效分析", """<h2>FMEA 失效模式与影响分析</h2>
<p>FMEA 用于系统识别潜在失效模式、评估风险、制定预防措施。</p>

<h3>操作步骤</h3>
<ol>
<li><b>添加分析项</b>：点击「+ 添加行」手动添加，或点击「📥 从HOQ导入CTQ」自动导入高优先级CTQ</li>
<li><b>填写失效信息</b>：
  <ul>
  <li>项目/功能：被分析的部件或功能</li>
  <li>潜在失效模式：可能发生什么故障？</li>
  <li>潜在失效后果：故障会造成什么影响？</li>
  <li>潜在失效原因：为什么会发生？</li>
  <li>现有控制措施：当前用什么方法预防/检测？</li>
  </ul>
</li>
<li><b>打分</b>（每项 1-10 分）：
  <ul>
  <li><b>S (严重度)</b>：故障后果有多严重？10=极其严重</li>
  <li><b>O (发生度)</b>：故障有多容易发生？10=经常发生</li>
  <li><b>D (探测度)</b>：故障有多难被发现？10=几乎无法检测</li>
  </ul>
</li>
<li><b>查看RPN</b>：系统自动计算 RPN = S × O × D</li>
</ol>

<h3>风险等级</h3>
<table border="1" cellpadding="4" style="border-collapse:collapse; width:100%;">
<tr style="background:#eee;"><th>RPN范围</th><th>等级</th><th>颜色</th><th>建议</th></tr>
<tr><td>≥ 200</td><td style="color:#E74C3C;font-weight:bold;">高风险</td><td style="background:#FADBD8;">红</td><td>必须立即采取纠正措施</td></tr>
<tr><td>100-199</td><td style="color:#E67E22;font-weight:bold;">中风险</td><td style="background:#FDEBD0;">橙</td><td>制定改进计划</td></tr>
<tr><td>50-99</td><td style="color:#F39C12;font-weight:bold;">低风险</td><td style="background:#FEF9E7;">黄</td><td>持续关注</td></tr>
<tr><td>< 50</td><td style="color:#27AE60;font-weight:bold;">可接受</td><td style="background:#D5F5E3;">绿</td><td>维持现状</td></tr>
</table>
<p>支持 DFMEA(设计) 和 PFMEA(工艺) 两种模式。可导出 CSV 报告。</p>
"""),

# ─── 8. DOE ───
("DOE 试验设计", """<h2>DOE 试验设计</h2>
<p>用于系统规划试验方案，以最少的试验次数获得最多信息。</p>

<h3>操作步骤</h3>
<ol>
<li><b>定义因子</b>：
  <ul>
  <li>因子名称：如"温度"、"压力"、"时间"</li>
  <li>水平值：逗号分隔，如 60,80,100</li>
  <li>点击「+ 添加因子」</li>
  </ul>
</li>
<li><b>选择设计类型</b>：
  <ul>
  <li><b>全因子设计</b>：所有水平的完全组合。如3个2水平因子 = 2×2×2 = 8次试验</li>
  <li><b>L8正交表</b>：适合2水平因子的简化设计，固定8次，最多7个因子</li>
  </ul>
</li>
<li>点击 <b>「📊 生成试验方案」</b></li>
<li>在方案表中填入试验结果 → 导出CSV用于进一步分析</li>
</ol>

<p><b>限制：</b>2-5个因子，每因子2-5个水平。</p>
"""),

# ─── 9. DSM ───
("DSM 结构矩阵", """<h2>DSM 设计结构矩阵</h2>
<p>DSM 是分析系统架构的工具，用于识别模块之间的依赖关系。</p>

<h3>操作步骤</h3>
<ol>
<li><b>添加元素</b>：点击「+ 添加元素」或「📥 从CTQ导入」</li>
<li><b>标记依赖</b>：点击矩阵格子，循环切换 空→<b>X</b>(依赖)→<b>?</b>(不确定)→空</li>
<li><b>分析结构</b>：点击「📊 分析依赖结构」</li>
</ol>

<h3>分析结果说明</h3>
<ul>
<li><b>密度</b>：依赖数 / 总可能关系数 的百分比</li>
<li><b>双向依赖(耦合)</b>：A→B 且 B→A，这对元素需要紧密协作、迭代设计</li>
<li><b>独立元素</b>：没有依赖关系，可以独立并行开发</li>
<li><b>高依赖节点</b>：被最多元素依赖的核心模块，需重点管理</li>
</ul>

<p><b>应用场景：</b>产品架构设计、团队组织结构、开发任务排序。</p>
"""),

# ─── 10. 授权说明 ───
("授权说明", """<h2>版本与授权</h2>
<h3>免费版</h3>
<p>包含HOQ等核心功能（VOC管理、CTQ管理、质量屋、竞争基准分析、项目管理、PNG导出）；个人永久免费。</p>
<h3>授权版（解锁全部功能）</h3>
<p>包含所有功能（Kano、AHP、Pareto、四阶段展开、TRIZ、FMEA、DOE、DSM、Excel/CSV导出、版本控制）；关注公众号即可免费获取授权码，仅限个人/非商业用途。</p>
<h3>商业版（解锁全部功能）</h3>
<p>包含所有功能，可用于商业用途；如需购买或定制，请联系 021-58108606。</p>

<h3>授权机制</h3>
<ul>
<li><b>云端在线验证</b>：激活时联网校验，成功后支持 30 天离线使用</li>
<li><b>一码一机</b>：每个授权码绑定一台电脑</li>
<li><b>可换机</b>：在原设备「取消激活」→ 新设备重新激活</li>
</ul>

<h3>激活步骤</h3>
<ol>
<li>点击菜单栏 <b>授权 → 授权管理...</b></li>
<li>输入授权码（格式: OQFD-XXXX-XXXX-XXXX-XXXX）</li>
<li>点击「激活」（需联网）→ 确认重启应用</li>
</ol>

<h3>换机步骤</h3>
<ol>
<li>旧电脑：授权 → 授权管理 → 「取消激活」（解绑授权码）</li>
<li>新电脑：授权 → 授权管理 → 输入同一授权码 → 激活</li>
</ol>

<p>💡 获取授权码请打开「授权 → 授权管理」页面查看联系方式。</p>
"""),

# ─── 11. 快捷操作 ───
("快捷操作", """<h2>快捷操作速查</h2>
<table border="1" cellpadding="5" style="border-collapse:collapse; width:100%;">
<tr style="background:#eee;"><th>位置</th><th>操作</th><th>效果</th></tr>
<tr><td>HOQ 关系矩阵</td><td>单击格子</td><td>循环: 空→△(1)→◎(3)→●(9)→空</td></tr>
<tr><td>HOQ 屋顶</td><td>单击菱形格</td><td>循环: 空→+→++→-→--→空</td></tr>
<tr><td>HOQ 右墙Ti列</td><td>双击黄色格子</td><td>手动编辑计划满意水平</td></tr>
<tr><td>DSM 矩阵</td><td>单击格子</td><td>循环: 空→X(依赖)→?(不确定)→空</td></tr>
<tr><td>VOC 树</td><td>⬆⬇ 按钮</td><td>调整需求排列顺序</td></tr>
<tr><td>VOC 搜索</td><td>搜索框</td><td>按名称搜索 + Kano类型过滤</td></tr>
<tr><td>阶段切换</td><td>侧栏顶部下拉框</td><td>切换四个QFD阶段</td></tr>
</table>
<h3>自动保存</h3>
<ul>
<li>每 60 秒自动保存当前项目</li>
<li>关闭软件时自动创建版本快照</li>
<li>可在「版本控制」中手动保存快照和回滚</li>
</ul>
<h3>数据导出</h3>
<ul>
<li><b>Excel(.xlsx)</b>：完整多Sheet报告</li>
<li><b>PNG</b>：质量屋矩阵截图</li>
<li><b>CSV</b>：FMEA报告、DOE方案</li>
<li><b>JSON</b>：完整项目数据备份</li>
</ul>
"""),
],


"en_US": [

("Quick Start", """<h2>Quick Start</h2>
<p><b>1.</b> Click <b>📁 New Project</b> or <b>📋 Load Demo</b></p>
<p><b>2.</b> Add customer needs in VOC module</p>
<p><b>3.</b> Add technical requirements in CTQ module</p>
<p><b>4.</b> Add competitors in Competition module (required for HOQ right wall)</p>
<p><b>5.</b> Fill the relationship matrix in HOQ (click cells to cycle ∅→△→◎→●)</p>
<p><b>6.</b> Edit Ti (planned level) in the yellow column of HOQ right wall</p>
<p><b>7.</b> Fill roof correlations (click diamonds to cycle ∅→+→++→-→--)</p>
<p style="color:#1565C0;"><b>💡 First time? Click "Load Demo" to explore with sample data.</b></p>"""),

("Build HOQ", """<h2>Step-by-Step: Build a Complete HOQ</h2>
<h3>Step 1: Enter VOC</h3><p>Add customer needs with importance scores (1-5).</p>
<h3>Step 2: Enter CTQ</h3><p>Add technical requirements with units and direction.</p>
<h3>Step 3: Add Competitors</h3>
<p>Add 2-4 competitors. Mark one as "Self". Fill VOC satisfaction scores (→ HOQ Ui column) and CTQ benchmarks (→ HOQ basement).</p>
<p><b>Without competitors, the right wall and basement will be empty!</b></p>
<h3>Step 4: Fill Relationship Matrix</h3>
<p>Click cells: ∅→△(1)→◎(3)→●(9)→∅. Only fill cells with actual relationships.</p>
<h3>Step 5: Set Planned Level (Ti)</h3>
<p>Double-click yellow Ti cells. Ri, Wai, Wi auto-calculate.</p>
<h3>Step 6: Fill Roof</h3>
<p>Click diamonds: ∅→+→++→-→--→∅. Mark CTQ-CTQ correlations.</p>
<p style="background:#E3F2FD;padding:8px;border-radius:6px;"><b>Done!</b> Your HOQ now has all 7 regions filled.</p>"""),

("HOQ Reference", """<h2>House of Quality Reference</h2>
<table border="1" cellpadding="5" style="border-collapse:collapse; width:100%;">
<tr style="background:#1565C0;color:white;"><th>Region</th><th>Content</th><th>Source</th></tr>
<tr><td>Roof</td><td>CTQ correlations</td><td>Manual click in HOQ</td></tr>
<tr><td>Ceiling</td><td>CTQ names/units/direction</td><td>CTQ module</td></tr>
<tr><td>Left Wall</td><td>VOC names + importance</td><td>VOC module</td></tr>
<tr><td>Room</td><td>Relationships ●◎△</td><td>Manual click in HOQ</td></tr>
<tr><td>Right Wall</td><td>Ui/Ti/Ri/Si/Wai/Wi + competitors</td><td>Competition + HOQ edit</td></tr>
<tr><td>Floor</td><td>Abs/Rel weights</td><td>Auto-calculated</td></tr>
<tr><td>Basement</td><td>Competitor CTQ benchmarks</td><td>Competition module</td></tr>
</table>
<p><b>Formulas:</b> Tai=Σ(rij×Ii), Ti=Tai/ΣTai, Ri=Ti/Ui, Wai=Ri×Si×Ii, M=Σ(Ii×score)/(ΣIi×max), T=Σ(Tai×norm)/ΣTai</p>"""),

("VOC & Kano", """<h2>VOC Management & Kano</h2>
<p>3-level tree, Excel/CSV import, Kano classification.</p>
<p><b>Key fields:</b> Importance Ii (1-5), Planned Level, Sales Point Si (1.0/1.2/1.5), Kano type.</p>"""),

("Advanced", """<h2>Advanced Analysis (Licensed)</h2>
<p><b>AHP:</b> Pairwise comparison → precise weights → consistency check (CR<0.1).</p>
<p><b>Pareto:</b> Bar chart + cumulative curve for CTQ prioritization.</p>
<p><b>4-Phase:</b> VOC→CTQ→Parts→Process→Production cascade.</p>"""),

("TRIZ", """<h2>TRIZ</h2>
<p><b>40 Principles:</b> Browse with Chinese/English descriptions.</p>
<p><b>Contradiction Matrix:</b> Select improving + worsening parameters → recommended principles.</p>"""),

("FMEA", """<h2>FMEA</h2>
<p>DFMEA/PFMEA. RPN = S×O×D. Risk: Red(≥200)/Orange(≥100)/Yellow(≥50)/Green(<50). Import CTQs from HOQ. Export CSV.</p>"""),

("DOE & DSM", """<h2>DOE & DSM</h2>
<p><b>DOE:</b> Define 2-5 factors, generate Full Factorial or L8 orthogonal design. Export CSV.</p>
<p><b>DSM:</b> N×N matrix, click ∅→X→?. Analyze coupling, independent elements, density.</p>"""),

("License", """<h2>Editions & Licensing</h2>
<h3>Free</h3>
<p>Core features (VOC, CTQ, HOQ, Competition, project management, PNG export); free forever for personal use.</p>
<h3>Licensed (all features unlocked)</h3>
<p>All features (Kano, AHP, Pareto, 4-Phase, TRIZ, FMEA, DOE, DSM, Excel/CSV export, Version Control); follow our WeChat account to get a free license key — for personal/noncommercial use only.</p>
<h3>Commercial (all features unlocked)</h3>
<p>All features, for commercial use; to purchase or request customization, contact 021-58108606.</p>
<p><b>One-Key-One-Machine.</b> Deactivate old device → re-activate new. 30-day offline grace.</p>
<p>💡 To get a license key, open "License → License Management" for contact details.</p>"""),

("Shortcuts", """<h2>Shortcuts</h2>
<ul>
<li>HOQ cells: click to cycle ∅→△→◎→●</li>
<li>Roof: ∅→+→++→-→--</li>
<li>Ti: double-click yellow cells</li>
<li>DSM: ∅→X→?</li>
<li>Auto-save every 60s, snapshot on close</li>
</ul>"""),
],
}


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("help.title"))
        self.setMinimumSize(860, 580)
        self.resize(980, 680)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        splitter = QSplitter(Qt.Horizontal)
        self.section_list = QListWidget()
        self.section_list.setFixedWidth(160)
        self.section_list.setStyleSheet("""
            QListWidget { background: #1B5E8C; border: none; font-size: 12px; }
            QListWidget::item { color: white; padding: 10px 10px; border-radius: 4px; margin: 1px 3px; }
            QListWidget::item:hover { background: #2980B9; }
            QListWidget::item:selected { background: #E67E22; font-weight: bold; }
        """)
        self.section_list.currentRowChanged.connect(self._on_changed)
        splitter.addWidget(self.section_list)
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setStyleSheet("QTextBrowser{background:white;border:none;padding:14px;font-size:13px;line-height:1.6;}")
        splitter.addWidget(self.browser)
        splitter.setSizes([160, 720])
        layout.addWidget(splitter)
        bar = QHBoxLayout()
        bar.setContentsMargins(10, 5, 10, 5)
        bar.addWidget(QLabel(t("help.contact_line", version=APP_VERSION)))
        bar.addStretch()
        btn = QPushButton(t("help.close"))
        btn.clicked.connect(self.accept)
        bar.addWidget(btn)
        layout.addLayout(bar)
        self._load()

    def _load(self):
        lang = get_language()
        sections = HELP_SECTIONS.get(lang, HELP_SECTIONS["zh_CN"])
        self.section_list.clear()
        self._html = []
        for title, html in sections:
            self.section_list.addItem(QListWidgetItem(f"  {title}"))
            self._html.append(html)
        if self._html:
            self.section_list.setCurrentRow(0)

    def _on_changed(self, row):
        if 0 <= row < len(self._html):
            self.browser.setHtml(self._html[row])
