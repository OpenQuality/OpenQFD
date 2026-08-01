"""
OpenQFD Internationalization (i18n) Module
Supports: zh_CN (Chinese, default), en_US (English)
"""
import json
import os
from pathlib import Path

_current_lang = "zh_CN"
_translations = {}

# ══════════════════════════════════════════════════════════════
#  Translation dictionaries
# ══════════════════════════════════════════════════════════════

LANGS = {
    "zh_CN": "中文",
    "en_US": "English",
}

_DICT = {
# ── App chrome ────────────────────────────────────────────────
"app.title":              {"zh_CN": "OpenQFD 质量功能展开软件", "en_US": "OpenQFD - Quality Function Deployment"},
"app.free":               {"zh_CN": "免费版", "en_US": "Free Edition"},
"app.licensed":           {"zh_CN": "授权版", "en_US": "Licensed Edition"},
"app.commercial":         {"zh_CN": "商业版", "en_US": "Commercial Edition"},
"app.ready":              {"zh_CN": "就绪 — 请创建或打开一个项目", "en_US": "Ready — Create or open a project"},
"app.subtitle":           {"zh_CN": "质量功能展开", "en_US": "Quality Function Deployment"},

# ── Sidebar nav ───────────────────────────────────────────────
"nav.overview":           {"zh_CN": "项目总览", "en_US": "Overview"},
"nav.voc":                {"zh_CN": "顾客需求 (VOC)", "en_US": "Voice of Customer (VOC)"},
"nav.ctq":                {"zh_CN": "质量特性（CTQ）", "en_US": "Critical To Quality (CTQ)"},
"nav.hoq":                {"zh_CN": "质量屋 (HOQ)", "en_US": "House of Quality (HOQ)"},
"nav.competition":        {"zh_CN": "竞争基准(CBA)", "en_US": "Competition Benchmarking Analysis (CBA)"},
"nav.kano":               {"zh_CN": "Kano 需求分类", "en_US": "Kano Classification"},
"nav.ahp":                {"zh_CN": "AHP 层次分析", "en_US": "AHP Analysis"},
"nav.pareto":             {"zh_CN": "Pareto 优先级", "en_US": "Pareto Priority"},
"nav.phase":              {"zh_CN": "四阶段展开", "en_US": "4-Phase Deployment"},
"nav.export":             {"zh_CN": "报告与导出", "en_US": "Reports & Export"},
"nav.version":            {"zh_CN": "版本控制", "en_US": "Version Control"},
"nav.back":               {"zh_CN": "返回首页", "en_US": "Back to Home"},
"nav.license":            {"zh_CN": "🔑 授权管理", "en_US": "🔑 License"},
"nav.help":               {"zh_CN": "📖 帮助手册", "en_US": "📖 Help Manual"},
"nav.lang":               {"zh_CN": "🌐 English", "en_US": "🌐 中文"},

# ── Project list ──────────────────────────────────────────────
"proj.title":             {"zh_CN": "OpenQFD 质量功能展开软件", "en_US": "OpenQFD - Quality Function Deployment"},
"proj.subtitle":          {"zh_CN": "将顾客之声转化为设计参数", "en_US": "Transform Voice of Customer into Design Parameters"},
"proj.new":               {"zh_CN": "📁 创建新项目", "en_US": "📁 New Project"},
"proj.demo":              {"zh_CN": "📋 加载示例项目", "en_US": "📋 Load Demo"},
"proj.import":            {"zh_CN": "📥 导入JSON项目", "en_US": "📥 Import JSON"},
"proj.list":              {"zh_CN": "📂 已有项目", "en_US": "📂 Projects"},
"proj.open":              {"zh_CN": "🚀 打开选中项目", "en_US": "🚀 Open Selected"},
"proj.delete":            {"zh_CN": "🗑 删除项目", "en_US": "🗑 Delete"},
"proj.select_first":      {"zh_CN": "请先选择一个项目", "en_US": "Please select a project first"},

# ── New project dialog ────────────────────────────────────────
"dlg.new_project":        {"zh_CN": "创建新项目", "en_US": "Create New Project"},
"dlg.name":               {"zh_CN": "项目名称:", "en_US": "Project Name:"},
"dlg.desc":               {"zh_CN": "描述:", "en_US": "Description:"},
"dlg.industry":           {"zh_CN": "行业:", "en_US": "Industry:"},
"dlg.scale":              {"zh_CN": "重要度量表:", "en_US": "Importance Scale:"},
"dlg.scale_5":            {"zh_CN": "5分制 (1-5)", "en_US": "5-point (1-5)"},
"dlg.scale_10":           {"zh_CN": "10分制 (1-10)", "en_US": "10-point (1-10)"},

# ── Phase names ───────────────────────────────────────────────
"phase.1":                {"zh_CN": "阶段一：产品规划", "en_US": "Phase 1: Product Planning"},
"phase.2":                {"zh_CN": "阶段二：零件展开", "en_US": "Phase 2: Part Deployment"},
"phase.3":                {"zh_CN": "阶段三：工艺规划", "en_US": "Phase 3: Process Planning"},
"phase.4":                {"zh_CN": "阶段四：生产控制", "en_US": "Phase 4: Production Control"},
"phase.short.1":          {"zh_CN": "产品规划", "en_US": "Product Planning"},
"phase.short.2":          {"zh_CN": "零件展开", "en_US": "Part Deployment"},
"phase.short.3":          {"zh_CN": "工艺规划", "en_US": "Process Planning"},
"phase.short.4":          {"zh_CN": "生产控制", "en_US": "Production Control"},
"phase.card_title":       {"zh_CN": "阶段 {n}", "en_US": "Phase {n}"},
"phase.row.1":            {"zh_CN": "顾客需求 (VOC)", "en_US": "Customer Needs (VOC)"},
"phase.row.2":            {"zh_CN": "质量特性（CTQ）", "en_US": "Quality Characteristics (CTQ)"},
"phase.row.3":            {"zh_CN": "零件特性", "en_US": "Part Characteristics"},
"phase.row.4":            {"zh_CN": "工艺参数", "en_US": "Process Parameters"},
"phase.col.1":            {"zh_CN": "质量特性（CTQ）", "en_US": "Quality Characteristics (CTQ)"},
"phase.col.2":            {"zh_CN": "零件特性", "en_US": "Part Characteristics"},
"phase.col.3":            {"zh_CN": "工艺参数", "en_US": "Process Parameters"},
"phase.col.4":            {"zh_CN": "生产控制措施", "en_US": "Production Controls"},
"phase.row_label":        {"zh_CN": "行: {v}", "en_US": "Row: {v}"},
"phase.col_label":        {"zh_CN": "列: {v}", "en_US": "Col: {v}"},

# ── VOC view ──────────────────────────────────────────────────
"voc.title":              {"zh_CN": "顾客需求 (VOC) 列表", "en_US": "Voice of Customer (VOC) List"},
"voc.add":                {"zh_CN": "+ 添加需求", "en_US": "+ Add VOC"},
"voc.add_child":          {"zh_CN": "+ 添加子需求", "en_US": "+ Add Child"},
"voc.import":             {"zh_CN": "📥 批量导入", "en_US": "📥 Batch Import"},
"voc.search":             {"zh_CN": "🔍 搜索需求...", "en_US": "🔍 Search..."},
"voc.all_kano":           {"zh_CN": "所有Kano类型", "en_US": "All Kano Types"},
"voc.detail":             {"zh_CN": "需求详情编辑", "en_US": "VOC Detail Editor"},
"voc.name":               {"zh_CN": "名称:", "en_US": "Name:"},
"voc.desc":               {"zh_CN": "描述:", "en_US": "Description:"},
"voc.source":             {"zh_CN": "来源:", "en_US": "Source:"},
"voc.importance":         {"zh_CN": "客户重要度:", "en_US": "Importance:"},
"voc.kano":               {"zh_CN": "Kano分类:", "en_US": "Kano Type:"},
"voc.improvement":        {"zh_CN": "改进比率:", "en_US": "Improvement Ratio:"},
"voc.sales_point":        {"zh_CN": "销售点:", "en_US": "Sales Point:"},
"voc.planned":            {"zh_CN": "计划水平:", "en_US": "Planned Level:"},
"voc.adj_weight":         {"zh_CN": "调整后权重:", "en_US": "Adjusted Weight:"},
"voc.save":               {"zh_CN": "💾 保存修改", "en_US": "💾 Save"},
"voc.delete":             {"zh_CN": "🗑 删除选中", "en_US": "🗑 Delete"},
"voc.count":              {"zh_CN": "共 {n} 条需求", "en_US": "{n} items"},
"voc.basic_info":         {"zh_CN": "基本信息", "en_US": "Basic Info"},
"voc.weight_settings":    {"zh_CN": "权重设置", "en_US": "Weight Settings"},

# ── CTQ view ──────────────────────────────────────────────────
"ctq.title":              {"zh_CN": "质量特性（CTQ）列表", "en_US": "Quality Characteristics (CTQ)"},
"ctq.add":                {"zh_CN": "+ 添加CTQ", "en_US": "+ Add CTQ"},
"ctq.delete":             {"zh_CN": "🗑 删除选中", "en_US": "🗑 Delete"},
"ctq.detail":             {"zh_CN": "CTQ 详情编辑", "en_US": "CTQ Detail"},
"ctq.unit":               {"zh_CN": "单位:", "en_US": "Unit:"},
"ctq.direction":          {"zh_CN": "优化方向:", "en_US": "Direction:"},
"ctq.target":             {"zh_CN": "目标值:", "en_US": "Target:"},
"ctq.current":            {"zh_CN": "当前值:", "en_US": "Current:"},
"ctq.difficulty":         {"zh_CN": "技术难度:", "en_US": "Difficulty:"},
"ctq.col_name":           {"zh_CN": "质量特性名称", "en_US": "CTQ Name"},
"ctq.col_unit":           {"zh_CN": "单位", "en_US": "Unit"},
"ctq.col_direction":      {"zh_CN": "方向", "en_US": "Direction"},
"ctq.col_current":        {"zh_CN": "当前值", "en_US": "Current"},
"ctq.col_target":         {"zh_CN": "目标值", "en_US": "Target"},
"ctq.col_difficulty":     {"zh_CN": "技术难度", "en_US": "Difficulty"},
"ctq.col_sort":           {"zh_CN": "排序", "en_US": "Order"},
"ctq.count":              {"zh_CN": "共 {n} 条CTQ", "en_US": "{n} items"},
"ctq.name_placeholder":   {"zh_CN": "质量特性名称", "en_US": "CTQ name"},
"ctq.unit_placeholder":   {"zh_CN": "如: mm, kg, %, ℃", "en_US": "e.g. mm, kg, %, °C"},
"ctq.current_placeholder": {"zh_CN": "当前值（基准）", "en_US": "Current value (baseline)"},
"ctq.target_placeholder": {"zh_CN": "目标值", "en_US": "Target value"},
"ctq.difficulty_tooltip": {"zh_CN": "1=容易 → 5=非常困难", "en_US": "1=Easy → 5=Very Difficult"},
"ctq.select_first":       {"zh_CN": "请先选择一条CTQ", "en_US": "Please select a CTQ item first"},
"ctq.new_item_name":      {"zh_CN": "新质量特性", "en_US": "New CTQ"},
"ctq.confirm_delete_body": {"zh_CN": "确定删除CTQ「{name}」？相关矩阵数据也将被清除。", "en_US": "Delete CTQ \"{name}\"? Related matrix data will also be cleared."},

# ── HOQ view ──────────────────────────────────────────────────
"hoq.title":              {"zh_CN": "质量屋 (House of Quality)", "en_US": "House of Quality (HOQ)"},
"hoq.strong":             {"zh_CN": "● 强相关(9)", "en_US": "● Strong(9)"},
"hoq.medium":             {"zh_CN": "◎ 中相关(3)", "en_US": "◎ Medium(3)"},
"hoq.weak":               {"zh_CN": "△ 弱相关(1)", "en_US": "△ Weak(1)"},
"hoq.symbol_mode":        {"zh_CN": "符号模式 (●◎△)", "en_US": "Symbol (●◎△)"},
"hoq.number_mode":        {"zh_CN": "数值模式 (9/3/1)", "en_US": "Numeric (9/3/1)"},
"hoq.recalc":             {"zh_CN": "🔄 重算", "en_US": "🔄 Recalc"},
"hoq.hint":               {"zh_CN": "💡 点击矩阵单元格循环: 空→△(1)→◎(3)→●(9)→空  |  点击屋顶钻石格循环: 空→+→++→-→--→空",
                           "en_US": "💡 Click cells to cycle: ∅→△(1)→◎(3)→●(9)→∅  |  Click roof diamonds: ∅→+→++→-→--→∅"},
"hoq.customer_req":       {"zh_CN": "客户需求  Ci", "en_US": "Customer Req.  Ci"},
"hoq.weight_ii":          {"zh_CN": "权重\nIi", "en_US": "Weight\nIi"},
"hoq.abs_weight":         {"zh_CN": "绝对权重 Tai", "en_US": "Abs. Weight Tai"},
"hoq.rel_weight":         {"zh_CN": "相对权重 Ti%", "en_US": "Rel. Weight Ti%"},
"hoq.rel_weight_row":     {"zh_CN": "相对权重 Ti", "en_US": "Rel. Weight Ti"},
"hoq.roof_legend_sp":     {"zh_CN": "++ 强正相关", "en_US": "++ Strong Positive"},
"hoq.roof_legend_p":      {"zh_CN": "+  正相关", "en_US": "+  Positive"},
"hoq.roof_legend_n":      {"zh_CN": "-  负相关", "en_US": "-  Negative"},
"hoq.roof_legend_sn":     {"zh_CN": "-- 强负相关", "en_US": "-- Strong Negative"},
"hoq.col_ui":             {"zh_CN": "Ui\n当前", "en_US": "Ui\nCurrent"},
"hoq.col_ti":             {"zh_CN": "Ti\n计划", "en_US": "Ti\nPlanned"},
"hoq.col_ri":             {"zh_CN": "Ri\nTi/Ui", "en_US": "Ri\nTi/Ui"},
"hoq.col_si":             {"zh_CN": "Si\n卖点", "en_US": "Si\nSales Pt"},
"hoq.col_wai":            {"zh_CN": "Wai\nRi*Si*Ii", "en_US": "Wai\nRi*Si*Ii"},
"hoq.col_wi":             {"zh_CN": "Wi\n归一化", "en_US": "Wi\nNormalized"},

# ── Competition ───────────────────────────────────────────────
"comp.title":             {"zh_CN": "竞争基准分析", "en_US": "Competition Benchmarking"},
"comp.add":               {"zh_CN": "+ 添加竞争对手", "en_US": "+ Add Competitor"},
"comp.delete":            {"zh_CN": "🗑 删除选中", "en_US": "🗑 Delete"},
"comp.radar":             {"zh_CN": "📊 生成雷达图", "en_US": "📊 Radar Chart"},
"comp.bar":               {"zh_CN": "📊 生成柱状对比图", "en_US": "📊 Bar Chart"},
"comp.col_name":          {"zh_CN": "竞争对手名称", "en_US": "Competitor Name"},
"comp.col_is_self":       {"zh_CN": "是否自身", "en_US": "Is Self"},
"comp.col_color":         {"zh_CN": "颜色标记", "en_US": "Color"},
"comp.tab_manage":        {"zh_CN": "🏢 竞争对手管理", "en_US": "🏢 Manage Competitors"},
"comp.voc_hint":          {"zh_CN": "💡 为每个竞争对手在各VOC维度上打分 (1-5分)", "en_US": "💡 Score each competitor on every VOC dimension (1-5)"},
"comp.tab_voc":           {"zh_CN": "📊 VOC评分基准", "en_US": "📊 VOC Scoring"},
"comp.ctq_hint":          {"zh_CN": "💡 录入各竞品在每个CTQ上的技术基准值", "en_US": "💡 Enter each competitor's technical benchmark value for every CTQ"},
"comp.tab_ctq":           {"zh_CN": "🔧 CTQ评分基准", "en_US": "🔧 CTQ Scoring"},
"comp.tab_chart":         {"zh_CN": "📈 对比图表", "en_US": "📈 Comparison Charts"},
"comp.is_self_mark":      {"zh_CN": "✓ 自身", "en_US": "✓ Self"},
"comp.limit_title":       {"zh_CN": "限制", "en_US": "Limit"},
"comp.max_competitors":   {"zh_CN": "最多支持5个竞争对手（含自身）", "en_US": "Maximum 5 competitors supported (including self)"},
"comp.our_product":       {"zh_CN": "我方产品", "en_US": "Our Product"},
"comp.competitor_n":      {"zh_CN": "竞品{n}", "en_US": "Competitor {n}"},
"comp.confirm_delete":    {"zh_CN": "删除竞争对手「{name}」？", "en_US": "Delete competitor \"{name}\"?"},
"comp.need_data_hint":    {"zh_CN": "请先添加竞争对手和VOC数据", "en_US": "Please add competitors and VOC data first"},
"comp.radar_title":       {"zh_CN": "竞争评估雷达图 (VOC维度)", "en_US": "Competitive Radar Chart (VOC Dimensions)"},
"comp.bar_xlabel":        {"zh_CN": "顾客需求", "en_US": "Customer Needs"},
"comp.bar_ylabel":        {"zh_CN": "客户评分 (1-5)", "en_US": "Customer Score (1-5)"},
"comp.bar_title":         {"zh_CN": "竞争基准对比", "en_US": "Competitive Benchmark Comparison"},

# ── Analysis ──────────────────────────────────────────────────
"ahp.title":              {"zh_CN": "AHP 层次分析法", "en_US": "AHP - Analytic Hierarchy Process"},
"ahp.compute":            {"zh_CN": "🔄 计算权重", "en_US": "🔄 Compute Weights"},
"ahp.apply":              {"zh_CN": "✅ 应用到HOQ", "en_US": "✅ Apply to HOQ"},
"kano.title":             {"zh_CN": "Kano 需求分类分析", "en_US": "Kano Classification"},
"kano.auto":              {"zh_CN": "🤖 自动分类建议", "en_US": "🤖 Auto-Classify"},
"kano.chart":             {"zh_CN": "📊 生成象限图", "en_US": "📊 Quadrant Chart"},
"pareto.title":           {"zh_CN": "Pareto 优先级分析", "en_US": "Pareto Priority Analysis"},
"pareto.generate":        {"zh_CN": "📊 生成Pareto图", "en_US": "📊 Generate Pareto"},

# ── AHP view ──────────────────────────────────────────────────
"ahp.hint":                {"zh_CN": "💡 AHP成对比较：比较两个需求的相对重要程度。值>1表示行比列更重要，<1表示列更重要。\n标度: 1=同等重要, 3=稍微重要, 5=明显重要, 7=强烈重要, 9=极端重要",
                            "en_US": "💡 AHP pairwise comparison: compare the relative importance of two items. Value>1 means row is more important than column, <1 means column is more important.\nScale: 1=Equal, 3=Slightly more, 5=Strongly more, 7=Very strongly more, 9=Extremely more"},
"ahp.result_group":        {"zh_CN": "计算结果", "en_US": "Results"},
"ahp.col_name":            {"zh_CN": "需求名称", "en_US": "Item Name"},
"ahp.col_weight":          {"zh_CN": "AHP权重", "en_US": "AHP Weight"},
"ahp.col_normalized":      {"zh_CN": "归一化(%)", "en_US": "Normalized (%)"},
"ahp.consistency_group":   {"zh_CN": "一致性检验", "en_US": "Consistency Check"},
"ahp.need_2_vocs":         {"zh_CN": "至少需要2条VOC才能进行AHP分析", "en_US": "At least 2 VOC items are required for AHP analysis"},
"ahp.consistent_ok":       {"zh_CN": "✅ 一致性检验通过 (CR < 0.1)\n\n权重计算可靠，可应用到HOQ。", "en_US": "✅ Consistency check passed (CR < 0.1)\n\nWeights are reliable and can be applied to HOQ."},
"ahp.consistent_fail":     {"zh_CN": "❌ 一致性检验未通过 (CR ≥ 0.1)\n\n", "en_US": "❌ Consistency check failed (CR ≥ 0.1)\n\n"},
"ahp.suggest_fix":         {"zh_CN": "建议修改: {a} vs {b}\n", "en_US": "Suggested fix: {a} vs {b}\n"},
"ahp.current_value":       {"zh_CN": "当前值: {v}\n", "en_US": "Current value: {v}\n"},
"ahp.suggested_value":     {"zh_CN": "建议值: {v}", "en_US": "Suggested value: {v}"},
"ahp.click_compute_first": {"zh_CN": "请先点击「🔄 计算权重」", "en_US": "Please click \"🔄 Compute Weights\" first"},
"ahp.applied_details_header": {"zh_CN": "以下VOC重要度已更新为AHP相对权重：\n\n", "en_US": "The following VOC importance values were updated to AHP relative weights:\n\n"},
"ahp.applied_title":       {"zh_CN": "✅ 已应用", "en_US": "✅ Applied"},
"ahp.applied_footer":      {"zh_CN": "\n权重按AHP相对比例设置（×10缩放）。\n切换到「📊 质量屋」查看更新后的权重。",
                            "en_US": "\nWeights set proportionally from AHP (×10 scaled).\nSwitch to \"📊 HOQ\" to see the updated weights."},

# ── Kano view ─────────────────────────────────────────────────
"kano.apply_adjusted":      {"zh_CN": "✅ 应用调整后重要度", "en_US": "✅ Apply Adjusted Importance"},
"kano.apply_tooltip":       {"zh_CN": "将「调整后重要度」(重要度×权重系数) 写回每条VOC的客户重要度，\n供质量屋(HOQ)的 Tai 计算等下游使用。默认不会自动应用。",
                            "en_US": "Writes \"Adjusted Importance\" (Importance × Kano multiplier) back into each VOC's customer importance,\nfor downstream use like HOQ's Tai calculation. Not applied automatically by default."},
"kano.col_name":            {"zh_CN": "需求名称", "en_US": "Item Name"},
"kano.col_type":            {"zh_CN": "Kano分类", "en_US": "Kano Type"},
"kano.col_importance":      {"zh_CN": "重要度", "en_US": "Importance"},
"kano.col_multiplier":      {"zh_CN": "权重调整系数", "en_US": "Weight Multiplier"},
"kano.col_adjusted":        {"zh_CN": "调整后重要度", "en_US": "Adjusted Importance"},
"kano.no_voc_data":         {"zh_CN": "当前没有VOC数据", "en_US": "No VOC data yet"},
"kano.confirm_apply_title": {"zh_CN": "确认应用", "en_US": "Confirm Apply"},
"kano.confirm_apply_body":  {"zh_CN": "这将用「调整后重要度」(重要度 × Kano权重系数) 覆盖每条VOC的客户重要度，\n原始重要度会被覆盖，且会影响质量屋(HOQ)的 Tai 计算。此操作不可撤销。\n\n是否继续？",
                            "en_US": "This will overwrite each VOC's customer importance with \"Adjusted Importance\" (Importance × Kano multiplier).\nThe original importance will be overwritten and this affects HOQ's Tai calculation. This cannot be undone.\n\nContinue?"},
"kano.applied_details_header": {"zh_CN": "以下VOC重要度已按Kano系数调整：\n\n", "en_US": "The following VOC importance values were adjusted by the Kano multiplier:\n\n"},
"kano.applied_title":       {"zh_CN": "✅ 已应用", "en_US": "✅ Applied"},
"kano.applied_footer":      {"zh_CN": "\n请切换到「📊 质量屋」查看更新后的 Tai 计算结果。", "en_US": "\nSwitch to \"📊 HOQ\" to see the updated Tai results."},
"kano.auto_done_title":     {"zh_CN": "自动分类完成", "en_US": "Auto-Classification Complete"},
"kano.auto_done_body":      {"zh_CN": "已自动分类 {n} 条需求。\n请人工审核并确认分类结果。", "en_US": "Auto-classified {n} items.\nPlease review and confirm the classification results."},
"kano.chart_xlabel":        {"zh_CN": "客户重要度", "en_US": "Customer Importance"},
"kano.chart_ylabel":        {"zh_CN": "Kano权重系数", "en_US": "Kano Weight Multiplier"},
"kano.chart_title":         {"zh_CN": "Kano需求分类象限图", "en_US": "Kano Classification Quadrant Chart"},

# ── Pareto view ───────────────────────────────────────────────
"pareto.sort_abs":          {"zh_CN": "按绝对重要度", "en_US": "By Absolute Importance"},
"pareto.sort_rel":          {"zh_CN": "按相对重要度", "en_US": "By Relative Importance"},
"pareto.sort_weighted":     {"zh_CN": "按加权重要度", "en_US": "By Weighted Importance"},
"pareto.sort_by":           {"zh_CN": "排序方式:", "en_US": "Sort By:"},
"pareto.need_ctq":          {"zh_CN": "请先添加CTQ数据", "en_US": "Please add CTQ data first"},
"pareto.cumulative_pct":    {"zh_CN": "累计百分比 (%)", "en_US": "Cumulative (%)"},
"pareto.line_80":           {"zh_CN": "80%线", "en_US": "80% line"},
"pareto.chart_title":       {"zh_CN": "CTQ技术重要度 Pareto图", "en_US": "CTQ Technical Importance Pareto Chart"},
"pareto.summary":           {"zh_CN": "📌 关键CTQ（前{n}项，二八法则）：{names}\n这些CTQ占总重要度的 {pct}%，应优先投入资源。",
                            "en_US": "📌 Key CTQs (top {n}, 80/20 rule): {names}\nThese CTQs account for {pct}% of total importance and should be prioritized."},

# ── Phase ─────────────────────────────────────────────────────
"phase.title":            {"zh_CN": "四阶段 QFD 展开", "en_US": "4-Phase QFD Deployment"},
"phase.cascade":          {"zh_CN": "▶ 阶段{a} → 阶段{b} 级联", "en_US": "▶ Phase {a} → Phase {b} Cascade"},
"phase.hint":             {"zh_CN": "💡 上游阶段的列(HOW)一键流转为下游阶段的行(WHAT)，实现级联传递",
                           "en_US": "💡 Upstream HOW columns cascade into downstream WHAT rows"},
"phase.cascade_group":    {"zh_CN": "级联流转操作", "en_US": "Cascade Operations"},
"phase.topology_group":   {"zh_CN": "关联拓扑视图", "en_US": "Topology View"},
"phase.detail_group":     {"zh_CN": "阶段详情", "en_US": "Phase Detail"},
"phase.open_edit":        {"zh_CN": "打开编辑", "en_US": "Open Editor"},
"phase.row_count":        {"zh_CN": "行: {n} 条", "en_US": "Rows: {n}"},
"phase.col_count":        {"zh_CN": "列: {n} 条", "en_US": "Cols: {n}"},
"phase.cascade_no_ctq":   {"zh_CN": "阶段{n}没有CTQ数据，无法级联", "en_US": "Phase {n} has no CTQ data — cannot cascade"},
"phase.cascade_confirm_body": {"zh_CN": "阶段{n}已有 {count} 条行数据，\n是否追加级联？（选择'否'则替换）",
                           "en_US": "Phase {n} already has {count} row items.\nAppend cascaded items? (Choose 'No' to replace)"},
"phase.cascade_desc":     {"zh_CN": "从阶段{n}级联: {name} (原重要度: {v}%)", "en_US": "Cascaded from Phase {n}: {name} (orig. importance: {v}%)"},
"phase.cascade_source":   {"zh_CN": "从阶段{n}级联", "en_US": "Cascaded from Phase {n}"},
"phase.cascade_done_title": {"zh_CN": "级联完成", "en_US": "Cascade Complete"},
"phase.cascade_done_body": {"zh_CN": "已将 {count} 个CTQ从阶段{a}流转到阶段{b}的行数据", "en_US": "Cascaded {count} CTQs from Phase {a} into Phase {b}'s rows"},
"phase.topology_title":   {"zh_CN": "四阶段QFD展开拓扑", "en_US": "4-Phase QFD Deployment Topology"},
"phase.detail_row_header": {"zh_CN": "行 ({v})", "en_US": "Row ({v})"},
"phase.detail_col_header": {"zh_CN": "列 ({v})", "en_US": "Col ({v})"},
"phase.importance":       {"zh_CN": "重要度", "en_US": "Importance"},
"phase.difficulty":       {"zh_CN": "技术难度", "en_US": "Difficulty"},
"phase.rowcol_count":     {"zh_CN": "行:{r} 列:{c}", "en_US": "Rows:{r} Cols:{c}"},

# ── Export ────────────────────────────────────────────────────
"export.title":           {"zh_CN": "报告与导出", "en_US": "Reports & Export"},
"export.excel":           {"zh_CN": "导出 Excel (.xlsx)", "en_US": "Export Excel (.xlsx)"},
"export.png":             {"zh_CN": "导出质量屋矩阵 (PNG)", "en_US": "Export HOQ Matrix (PNG)"},
"export.fmea":            {"zh_CN": "导出 FMEA CTQ清单 (CSV)", "en_US": "Export FMEA CTQ List (CSV)"},
"export.json":            {"zh_CN": "导出项目数据 (JSON)", "en_US": "Export Project Data (JSON)"},
"export.excel_group":     {"zh_CN": "📊 Excel 导出", "en_US": "📊 Excel Export"},
"export.excel_desc":      {"zh_CN": "导出包含所有矩阵数据、计算结果的Excel文件，保留完整数据结构。", "en_US": "Export an Excel file with all matrix data and computed results, preserving the full data structure."},
"export.png_group":       {"zh_CN": "🖼 PNG/SVG 图片导出", "en_US": "🖼 PNG/SVG Image Export"},
"export.png_desc":        {"zh_CN": "导出质量屋矩阵和分析图表为高清图片。", "en_US": "Export the HOQ matrix and analysis charts as high-resolution images."},
"export.fmea_group":      {"zh_CN": "🔧 FMEA 数据导出", "en_US": "🔧 FMEA Data Export"},
"export.fmea_desc":       {"zh_CN": "将高优先级CTQ导出为CSV格式，作为FMEA分析的输入。", "en_US": "Export high-priority CTQs as CSV, for use as FMEA analysis input."},
"export.json_group":      {"zh_CN": "💾 项目数据备份", "en_US": "💾 Project Data Backup"},
"export.json_desc":       {"zh_CN": "导出完整项目数据为JSON文件，可用于数据备份和迁移。", "en_US": "Export the full project data as a JSON file, for backup and migration."},
"export.dlg_excel_title": {"zh_CN": "导出Excel", "en_US": "Export Excel"},
"export.excel_filter":    {"zh_CN": "Excel文件 (*.xlsx)", "en_US": "Excel Files (*.xlsx)"},
"export.sheet_voc":       {"zh_CN": "VOC顾客需求", "en_US": "VOC Customer Needs"},
"export.sheet_ctq":       {"zh_CN": "CTQ质量特性", "en_US": "CTQ Quality Characteristics"},
"export.sheet_rel":       {"zh_CN": "关系矩阵", "en_US": "Relationship Matrix"},
"export.sheet_importance": {"zh_CN": "技术重要度", "en_US": "Technical Importance"},
"export.h_id":            {"zh_CN": "ID", "en_US": "ID"},
"export.h_name":          {"zh_CN": "需求名称", "en_US": "Name"},
"export.h_desc":          {"zh_CN": "描述", "en_US": "Description"},
"export.h_source":        {"zh_CN": "来源", "en_US": "Source"},
"export.h_importance":    {"zh_CN": "重要度", "en_US": "Importance"},
"export.h_kano_type":     {"zh_CN": "Kano分类", "en_US": "Kano Type"},
"export.h_improvement":   {"zh_CN": "改进比", "en_US": "Improvement Ratio"},
"export.h_sales_point":   {"zh_CN": "销售点", "en_US": "Sales Point"},
"export.h_ctq_name":      {"zh_CN": "质量特性", "en_US": "CTQ Name"},
"export.h_unit":          {"zh_CN": "单位", "en_US": "Unit"},
"export.h_direction":     {"zh_CN": "方向", "en_US": "Direction"},
"export.h_target":        {"zh_CN": "目标值", "en_US": "Target"},
"export.h_current":       {"zh_CN": "当前值", "en_US": "Current"},
"export.h_difficulty":    {"zh_CN": "技术难度", "en_US": "Difficulty"},
"export.h_abs_importance": {"zh_CN": "绝对重要度", "en_US": "Absolute Importance"},
"export.h_rel_importance": {"zh_CN": "相对重要度(%)", "en_US": "Relative Importance (%)"},
"export.h_weighted_importance": {"zh_CN": "加权重要度", "en_US": "Weighted Importance"},
"export.h_rank":          {"zh_CN": "优先排名", "en_US": "Priority Rank"},
"export.h_voc_vs_ctq":    {"zh_CN": "VOC \\ CTQ", "en_US": "VOC \\ CTQ"},
"export.excel_success":   {"zh_CN": "Excel报告已导出到:\n{path}", "en_US": "Excel report exported to:\n{path}"},
"export.dlg_png_title":   {"zh_CN": "导出PNG", "en_US": "Export PNG"},
"export.png_filter":      {"zh_CN": "PNG图片 (*.png);;SVG图片 (*.svg)", "en_US": "PNG Images (*.png);;SVG Images (*.svg)"},
"export.empty_matrix":    {"zh_CN": "矩阵为空，无法导出", "en_US": "Matrix is empty — nothing to export"},
"export.png_title":       {"zh_CN": "质量屋 - 关系矩阵", "en_US": "House of Quality - Relationship Matrix"},
"export.png_colorbar":    {"zh_CN": "关系强度", "en_US": "Relationship Strength"},
"export.png_success":     {"zh_CN": "图片已导出到:\n{path}", "en_US": "Image exported to:\n{path}"},
"export.dlg_fmea_title":  {"zh_CN": "导出FMEA CTQ清单", "en_US": "Export FMEA CTQ List"},
"export.h_ctq_id":        {"zh_CN": "CTQ编号", "en_US": "CTQ ID"},
"export.h_is_key_ctq":    {"zh_CN": "是否关键CTQ", "en_US": "Key CTQ"},
"export.yes":             {"zh_CN": "是", "en_US": "Yes"},
"export.no":              {"zh_CN": "否", "en_US": "No"},
"export.fmea_success":    {"zh_CN": "FMEA CTQ清单已导出到:\n{path}", "en_US": "FMEA CTQ list exported to:\n{path}"},
"export.dlg_json_title":  {"zh_CN": "导出项目数据", "en_US": "Export Project Data"},
"export.json_success":    {"zh_CN": "项目数据已导出到:\n{path}", "en_US": "Project data exported to:\n{path}"},
"export.export_failed":   {"zh_CN": "导出失败", "en_US": "Export Failed"},

# ── Version ───────────────────────────────────────────────────
"ver.title":              {"zh_CN": "版本控制", "en_US": "Version Control"},
"ver.save":               {"zh_CN": "📌 保存版本快照", "en_US": "📌 Save Snapshot"},
"ver.label":              {"zh_CN": "版本标签:", "en_US": "Version Label:"},
"ver.hint":               {"zh_CN": "💡 版本快照记录项目完整状态，支持对比和回滚到历史版本", "en_US": "💡 Version snapshots record the project's full state, supporting comparison and rollback"},
"ver.label_placeholder":  {"zh_CN": "如: V1.0评审稿、初稿 等自定义标识", "en_US": "e.g. V1.0 Review Draft, First Draft, etc."},
"ver.col_id":             {"zh_CN": "版本ID", "en_US": "Version ID"},
"ver.col_label":          {"zh_CN": "标签", "en_US": "Label"},
"ver.col_created":        {"zh_CN": "创建时间", "en_US": "Created At"},
"ver.col_actions":        {"zh_CN": "操作", "en_US": "Actions"},
"ver.detail_group":       {"zh_CN": "版本快照详情", "en_US": "Snapshot Detail"},
"ver.auto_save_label":    {"zh_CN": "自动保存 #{id}", "en_US": "Auto-save #{id}"},
"ver.view_btn":           {"zh_CN": "查看", "en_US": "View"},
"ver.restore_btn":        {"zh_CN": "回滚", "en_US": "Restore"},
"ver.saved_success":      {"zh_CN": "版本快照已保存", "en_US": "Version snapshot saved"},
"ver.detail_project":     {"zh_CN": "项目: {v}\n", "en_US": "Project: {v}\n"},
"ver.detail_voc_count":   {"zh_CN": "VOC数量: {v}\n", "en_US": "VOC count: {v}\n"},
"ver.detail_ctq_count":   {"zh_CN": "CTQ数量: {v}\n", "en_US": "CTQ count: {v}\n"},
"ver.detail_rel_count":   {"zh_CN": "关系数据: {v} 条\n", "en_US": "Relationships: {v}\n"},
"ver.detail_roof_count":  {"zh_CN": "屋顶数据: {v} 条\n", "en_US": "Roof correlations: {v}\n"},
"ver.detail_comp_count":  {"zh_CN": "竞争对手: {v} 个\n", "en_US": "Competitors: {v}\n"},
"ver.confirm_restore_title": {"zh_CN": "确认回滚", "en_US": "Confirm Restore"},
"ver.confirm_restore_body": {"zh_CN": "回滚将用历史版本覆盖当前数据，此操作不可撤销。\n\n建议先保存当前版本快照。\n\n确定回滚？",
                           "en_US": "Restoring will overwrite current data with the historical version. This cannot be undone.\n\nConsider saving a snapshot of the current state first.\n\nProceed with restore?"},
"ver.restored_success":   {"zh_CN": "已回滚到选中的历史版本", "en_US": "Restored to the selected historical version"},

# ── License dialog ────────────────────────────────────────────
"lic.title":              {"zh_CN": "授权管理", "en_US": "License Management"},
"lic.current":            {"zh_CN": "当前授权状态", "en_US": "Current License Status"},
"lic.status_free":        {"zh_CN": "免费版：包含HOQ等核心功能；个人永久免费；关注微信公众号「OpenQuality」自动获取授权码，解锁所有功能。",
                           "en_US": "Free: Includes core features like HOQ; free forever for personal use; follow the WeChat account \"OpenQuality\" to automatically get a license key and unlock all features."},
"lic.status_licensed":    {"zh_CN": "授权版：包含所有功能，仅用于个人/非商业用途；如需商用，请联系{contact}。",
                           "en_US": "Licensed: Includes all features, for personal/noncommercial use only; for commercial use, contact {contact}."},
"lic.status_commercial":  {"zh_CN": "商业版：包含所有功能及售后服务，可用于商业用途；如需定制，请联系{contact}。",
                           "en_US": "Commercial: Includes all features plus after-sales support, and may be used commercially; for customization, contact {contact}."},
"lic.key_line":           {"zh_CN": "授权码: {lic_key}　{online_tag}", "en_US": "Key: {lic_key}   {online_tag}"},
"lic.activate":           {"zh_CN": "🔑 激活", "en_US": "🔑 Activate"},
"lic.deactivate":         {"zh_CN": "取消激活 (回到免费版)", "en_US": "Deactivate (revert to Free)"},
"lic.activate_section":   {"zh_CN": "激活授权码", "en_US": "Activate License Key"},
"lic.purchase":           {"zh_CN": "购买授权", "en_US": "Purchase License"},
"lic.enter_key":          {"zh_CN": "输入授权码 (格式: OQFD-XXXX-XXXX-XXXX-XXXX):", "en_US": "Enter license key (format: OQFD-XXXX-XXXX-XXXX-XXXX):"},

# ── Common ────────────────────────────────────────────────────
"common.confirm":         {"zh_CN": "确认", "en_US": "Confirm"},
"common.cancel":          {"zh_CN": "取消", "en_US": "Cancel"},
"common.close":           {"zh_CN": "关闭", "en_US": "Close"},
"common.success":         {"zh_CN": "成功", "en_US": "Success"},
"common.error":           {"zh_CN": "错误", "en_US": "Error"},
"common.hint":            {"zh_CN": "提示", "en_US": "Info"},
"common.save":            {"zh_CN": "💾 保存修改", "en_US": "💾 Save"},
"common.confirm_delete":  {"zh_CN": "确定删除？", "en_US": "Confirm deletion?"},
"common.up":              {"zh_CN": "⬆ 上移", "en_US": "⬆ Up"},
"common.down":            {"zh_CN": "⬇ 下移", "en_US": "⬇ Down"},
"common.quick_actions":   {"zh_CN": "快速操作", "en_US": "Quick Actions"},

# ── Kano types ────────────────────────────────────────────────
"kano.must_be":           {"zh_CN": "基本型 (Must-be)", "en_US": "Must-be"},
"kano.one_dim":           {"zh_CN": "期望型 (One-dimensional)", "en_US": "One-dimensional"},
"kano.attractive":        {"zh_CN": "魅力型 (Attractive)", "en_US": "Attractive"},
"kano.indifferent":       {"zh_CN": "无差异型 (Indifferent)", "en_US": "Indifferent"},
"kano.reverse":           {"zh_CN": "逆向型 (Reverse)", "en_US": "Reverse"},
"kano.unclassified":      {"zh_CN": "未分类", "en_US": "Unclassified"},

# ── Directions ────────────────────────────────────────────────
"dir.higher":             {"zh_CN": "↑ 越大越好", "en_US": "↑ Higher is better"},
"dir.lower":              {"zh_CN": "↓ 越小越好", "en_US": "↓ Lower is better"},
"dir.target":             {"zh_CN": "◎ 目标值型", "en_US": "◎ Target value"},

# ── Industries ────────────────────────────────────────────────
"ind.auto":               {"zh_CN": "汽车制造", "en_US": "Automotive"},
"ind.electronics":        {"zh_CN": "消费电子", "en_US": "Consumer Electronics"},
"ind.software":           {"zh_CN": "软件开发", "en_US": "Software"},
"ind.medical":            {"zh_CN": "医疗器械", "en_US": "Medical Devices"},
"ind.service":            {"zh_CN": "服务业", "en_US": "Services"},
"ind.aerospace":          {"zh_CN": "航空航天", "en_US": "Aerospace"},
"ind.food":               {"zh_CN": "食品饮料", "en_US": "Food & Beverage"},
"ind.general":            {"zh_CN": "通用制造", "en_US": "General Manufacturing"},
"ind.other":              {"zh_CN": "其他", "en_US": "Other"},

# ── VOC sources ───────────────────────────────────────────────
"src.research":           {"zh_CN": "市场调研", "en_US": "Market Research"},
"src.interview":          {"zh_CN": "客户访谈", "en_US": "Customer Interview"},
"src.complaint":          {"zh_CN": "投诉反馈", "en_US": "Complaint Feedback"},
"src.standard":           {"zh_CN": "行业标准", "en_US": "Industry Standard"},
"src.benchmark":          {"zh_CN": "竞品分析", "en_US": "Competitive Analysis"},
"src.internal":           {"zh_CN": "内部建议", "en_US": "Internal Suggestion"},

# ── Help manual ───────────────────────────────────────────────
"help.title":             {"zh_CN": "OpenQFD 帮助手册", "en_US": "OpenQFD Help Manual"},
"help.close":             {"zh_CN": "关闭", "en_US": "Close"},

# ── main.py: License dialog ─────────────────────────────────────
"lic.online_verified":    {"zh_CN": "🌐 在线验证", "en_US": "🌐 Verified Online"},
"lic.offline_cache":      {"zh_CN": "💾 离线缓存 (剩余{grace}天)", "en_US": "💾 Offline Cache ({grace} days left)"},
"lic.checking_server":    {"zh_CN": "🔍 检测授权服务器...", "en_US": "🔍 Checking license server..."},
"lic.features_body":      {"zh_CN": "{purchase_info}\n\n⚡ 在线激活，授权码一键生效；如需换机可解绑后再绑定新机器。",
                           "en_US": "{purchase_info}\n\n⚡ Online activation — instant effect with one click; to switch devices, deactivate then bind the new one."},
"lic.server_ok":          {"zh_CN": "✅ 授权服务器连接正常", "en_US": "✅ License server connected"},
"lic.server_fail":        {"zh_CN": "⚠️ 授权服务器无法连接（请检查网络）", "en_US": "⚠️ Cannot reach license server (check network)"},
"lic.enter_key_warning":  {"zh_CN": "请输入授权码 / Please enter a license key", "en_US": "Please enter a license key"},
"lic.format_error":       {"zh_CN": "授权码格式不正确\n\n正确格式 / Format: OQFD-XXXX-XXXX-XXXX-XXXX\n\n{purchase_info}",
                           "en_US": "Invalid license key format\n\nFormat: OQFD-XXXX-XXXX-XXXX-XXXX\n\n{purchase_info}"},
"lic.activating":         {"zh_CN": "⏳ 正在激活...", "en_US": "⏳ Activating..."},
"lic.activated_msg":      {"zh_CN": "🎉 授权版已激活！/ Commercial activated!\n授权码已绑定到本机。\nKey bound to this device.\n\n是否立即刷新界面以生效？\nRefresh the interface now to take effect?",
                           "en_US": "🎉 Licensed Edition activated!\nKey bound to this device.\n\nRefresh the interface now to take effect?"},
"lic.already_bound_short":{"zh_CN": "❌ 该授权码已绑定其他设备", "en_US": "❌ Key already bound to another device"},
"lic.already_bound_full": {"zh_CN": "该授权码已在另一台设备上激活。\nThis key is already activated on another device.\n\n请先在原设备上「取消激活」，或联系管理员解绑。\nDeactivate on the old device first, or contact admin.\n\n{purchase_info}",
                           "en_US": "This key is already activated on another device.\n\nDeactivate on the old device first, or contact admin.\n\n{purchase_info}"},
"lic.activate_fail":      {"zh_CN": "激活失败 / Activation failed\n\n{message}\n\n{purchase_info}", "en_US": "Activation failed\n\n{message}\n\n{purchase_info}"},
"lic.deactivate_confirm": {"zh_CN": "确定取消激活？\n取消后，此授权码可在其他设备上重新激活。\n\nDeactivate? The key can then be activated on another device.",
                           "en_US": "Deactivate? The key can then be activated on another device."},
"lic.deactivated_msg":    {"zh_CN": "授权已取消，授权码已解绑。\n是否立即刷新界面以生效？\nDeactivated and unbound. Refresh the interface now to take effect?",
                           "en_US": "Deactivated and unbound. Refresh the interface now to take effect?"},

# ── main.py: New project / project picker dialogs ────────────────
"dlg.name_placeholder":   {"zh_CN": "例: 新能源汽车空调系统QFD", "en_US": "e.g. EV HVAC System QFD"},
"dlg.desc_placeholder":   {"zh_CN": "项目描述...", "en_US": "Project description..."},
"dlg.unnamed_project":    {"zh_CN": "未命名项目", "en_US": "Untitled Project"},
"proj.open_title":        {"zh_CN": "打开项目", "en_US": "Open Project"},
"proj.delete_title":      {"zh_CN": "删除项目", "en_US": "Delete Project"},
"proj.row_line":          {"zh_CN": "📊 {name}  |  {industry}  |  更新于: {updated_at}", "en_US": "📊 {name}  |  {industry}  |  Updated: {updated_at}"},
"proj.no_projects_hint":  {"zh_CN": "暂无项目，请先在「文件」菜单中创建新项目或新建示例项目。", "en_US": "No projects yet — create one or a sample project from the File menu."},
"proj.open_btn":          {"zh_CN": "打开", "en_US": "Open"},
"proj.delete_btn":        {"zh_CN": "删除", "en_US": "Delete"},
"proj.none_placeholder":  {"zh_CN": "（暂无项目）", "en_US": "(No projects)"},

# ── main.py: Update check / menu / about ──────────────────────────
"update.available_title": {"zh_CN": "发现新版本 / Update available", "en_US": "Update available"},
"update.available_body":  {"zh_CN": "发现新版本 V{version}（当前版本 V{current}）。{notes}\n\n是否前往下载？下载完成后关闭本软件，用新的 exe 文件覆盖旧文件即可。\n",
                           "en_US": "New version V{version} available (current V{current}). {notes}\n\nGo to download page? After downloading, close this app and overwrite the old exe.\n"},
"update.no_link":         {"zh_CN": "未配置下载链接，请稍后重试。", "en_US": "No download link configured. Please try again later."},
"update.notes_prefix":    {"zh_CN": "\n\n更新内容:\n{body}", "en_US": "\n\nRelease notes:\n{body}"},
"menu.file":               {"zh_CN": "文件(&F)", "en_US": "&File"},
"menu.new_project":        {"zh_CN": "📁 新建项目...", "en_US": "📁 New Project..."},
"menu.open_project":       {"zh_CN": "🚀 打开项目...", "en_US": "🚀 Open Project..."},
"menu.switch_project":     {"zh_CN": "🔀 切换项目", "en_US": "🔀 Switch Project"},
"menu.new_demo":           {"zh_CN": "📋 新建示例项目", "en_US": "📋 New Sample Project"},
"menu.import_project":     {"zh_CN": "📥 导入JSON项目...", "en_US": "📥 Import JSON Project..."},
"menu.delete_project":     {"zh_CN": "🗑 删除项目...", "en_US": "🗑 Delete Project..."},
"menu.back_home":          {"zh_CN": "⬅ 返回首页", "en_US": "⬅ Back to Home"},
"menu.exit":               {"zh_CN": "退出", "en_US": "Exit"},
"menu.license":            {"zh_CN": "授权(&L)", "en_US": "&License"},
"menu.license_manage":     {"zh_CN": "授权管理...", "en_US": "License Management..."},
"menu.help":               {"zh_CN": "帮助(&H)", "en_US": "&Help"},
"menu.help_manual":        {"zh_CN": "帮助手册", "en_US": "Help Manual"},
"menu.about":              {"zh_CN": "关于 OpenQFD", "en_US": "About OpenQFD"},
"about.body":              {"zh_CN": "OpenQFD — 质量功能展开软件\n版本: V{version} ({edition})\n\n整合 VOC / CTQ / HOQ / Kano / AHP / Pareto / TRIZ / FMEA / DOE / DSM\n十大质量工具，将顾客之声系统性转化为工程决策。",
                           "en_US": "OpenQFD — Quality Function Deployment Software\nVersion: V{version} ({edition})\n\nIntegrates VOC / CTQ / HOQ / Kano / AHP / Pareto / TRIZ / FMEA / DOE / DSM\n— ten quality tools turning Voice of Customer into engineering decisions."},
"badge.licensed":         {"zh_CN": "授权版", "en_US": "Licensed"},
"badge.free":             {"zh_CN": "免费版", "en_US": "Free"},
"nav.triz":               {"zh_CN": "TRIZ 发明原理", "en_US": "TRIZ Principles"},
"nav.fmea":               {"zh_CN": "FMEA 失效分析", "en_US": "FMEA Analysis"},
"nav.doe":                {"zh_CN": "DOE 试验设计", "en_US": "DOE Design"},
"nav.dsm":                {"zh_CN": "DSM 结构矩阵", "en_US": "DSM Matrix"},

# ── main.py: Overview page ────────────────────────────────────────
"overview.voc_count":     {"zh_CN": "VOC需求", "en_US": "VOC Items"},
"overview.ctq_count":     {"zh_CN": "CTQ特性", "en_US": "CTQ Items"},
"overview.rel_count":     {"zh_CN": "关系数据", "en_US": "Relationships"},
"overview.comp_count":    {"zh_CN": "竞争对手", "en_US": "Competitors"},
"overview.market_index":  {"zh_CN": "🛒 市场竞争指数 M", "en_US": "🛒 Market Competitive Index M"},
"overview.market_index_desc": {"zh_CN": "客户满意度 (来自竞争基准CBA)", "en_US": "Customer satisfaction (from CBA)"},
"overview.tech_index":    {"zh_CN": "⚙️ 技术竞争指数 T", "en_US": "⚙️ Technical Competitive Index T"},
"overview.tech_index_desc": {"zh_CN": "技术基准竞争力 (来自质量屋HOQ)", "en_US": "Technical benchmark strength (from HOQ)"},
"overview.hoq_output":    {"zh_CN": "📈 HOQ 核心决策输出", "en_US": "📈 HOQ Key Decision Output"},
"overview.readiness":     {"zh_CN": "✅ 项目就绪度检查", "en_US": "✅ Project Readiness Check"},
"overview.quick_actions": {"zh_CN": "⚡ 快速操作", "en_US": "⚡ Quick Actions"},
"overview.manage_voc":    {"zh_CN": "📋 管理VOC", "en_US": "📋 Manage VOC"},
"overview.manage_ctq":    {"zh_CN": "🔧 管理CTQ", "en_US": "🔧 Manage CTQ"},
"overview.edit_hoq":      {"zh_CN": "📊 编辑质量屋", "en_US": "📊 Edit HOQ"},
"overview.export_report": {"zh_CN": "📤 导出报告", "en_US": "📤 Export Report"},
"overview.no_self_hint":  {"zh_CN": "请先在「竞争基准 CBA」中配置「我方产品」并录入评分", "en_US": "Set up \"Our Product\" and scores in Competition (CBA) first"},
"overview.no_data_hint":  {"zh_CN": "暂无数据，请先添加 VOC 和 CTQ", "en_US": "No data yet — add VOC and CTQ items first"},
"overview.no_voc_hint":   {"zh_CN": "暂无VOC数据", "en_US": "No VOC data yet"},
"overview.no_rel_hint":   {"zh_CN": "请先填写质量屋关系矩阵", "en_US": "Fill in the HOQ relationship matrix first"},
"readiness.voc":          {"zh_CN": "VOC 顾客需求已录入（{n} 条）", "en_US": "VOC entered ({n} items)"},
"readiness.ctq":          {"zh_CN": "CTQ 质量特性已录入（{n} 条）", "en_US": "CTQ entered ({n} items)"},
"readiness.rel":          {"zh_CN": "质量屋关系矩阵已填写（{n} 个关系）", "en_US": "HOQ relationship matrix filled ({n} relationships)"},
"readiness.comp":         {"zh_CN": "竞争基准已配置（{n} 个竞品）", "en_US": "Competition benchmark set up ({n} competitors)"},

# ── main.py: status / misc messages ───────────────────────────────
"msg.no_project_first":   {"zh_CN": "请先在「文件」菜单创建或打开一个项目", "en_US": "Please create or open a project from the File menu first"},
"msg.project_opened":     {"zh_CN": "已打开项目: {name}", "en_US": "Opened project: {name}"},
"msg.confirm_delete_title": {"zh_CN": "确认删除", "en_US": "Confirm Delete"},
"msg.confirm_delete_project": {"zh_CN": "确定删除项目「{name}」？所有数据将永久丢失。", "en_US": "Delete project \"{name}\"? All data will be permanently lost."},
"msg.import_project_title": {"zh_CN": "导入项目", "en_US": "Import Project"},
"msg.import_json_filter": {"zh_CN": "JSON文件 (*.json)", "en_US": "JSON Files (*.json)"},
"msg.import_complete":    {"zh_CN": "项目导入完成", "en_US": "Project import complete"},
"msg.import_failed":      {"zh_CN": "导入失败", "en_US": "Import Failed"},
"msg.demo_title":         {"zh_CN": "示例项目", "en_US": "Sample Project"},
"msg.demo_created":       {"zh_CN": "已新建「{name}」示例项目，\n包含8条VOC、8条CTQ、关系矩阵和竞品数据。", "en_US": "Created sample project \"{name}\",\nwith 8 VOCs, 8 CTQs, relationship matrix, and competitor data."},
"msg.auto_saved":         {"zh_CN": "已自动保存", "en_US": "Auto-saved"},
"msg.auto_save_version":  {"zh_CN": "自动保存（关闭时）", "en_US": "Auto-save (on close)"},
"project.industry_line":  {"zh_CN": "行业: {v}  |  ", "en_US": "Industry: {v}  |  "},
"project.scale_line":     {"zh_CN": "重要度量表: {v}分制  |  ", "en_US": "Importance Scale: {v}-point  |  "},
"project.created_line":   {"zh_CN": "创建时间: {v}  |  ", "en_US": "Created: {v}  |  "},
"project.updated_line":   {"zh_CN": "最后更新: {v}\n", "en_US": "Last Updated: {v}\n"},
"project.desc_line":      {"zh_CN": "描述: {v}", "en_US": "Description: {v}"},
"project.no_desc":        {"zh_CN": "暂无描述", "en_US": "No description"},
"phase.status":           {"zh_CN": "当前阶段: {name}", "en_US": "Current phase: {name}"},
"lang.confirm_title":     {"zh_CN": "Language / 语言", "en_US": "Language / 语言"},
"lang.confirm_body":      {"zh_CN": "语言已切换，是否立即刷新界面？\nLanguage changed. Refresh the interface now?",
                           "en_US": "Language changed. Refresh the interface now?"},
"overview.no_data_chart": {"zh_CN": "暂无数据，请先添加 VOC 和 CTQ", "en_US": "No data yet — add VOC and CTQ items first"},
"overview.kano_dist":     {"zh_CN": "VOC Kano类型分布", "en_US": "VOC Kano Type Distribution"},
"overview.no_voc_chart":  {"zh_CN": "暂无VOC数据", "en_US": "No VOC data yet"},
"overview.top5_voc":      {"zh_CN": "Top 5 优先VOC (右墙 Wai)", "en_US": "Top 5 Priority VOC (Right Wall Wai)"},
"overview.no_rel_chart":  {"zh_CN": "请先填写质量屋关系矩阵", "en_US": "Fill in the HOQ relationship matrix first"},
"overview.top5_ctq":      {"zh_CN": "Top 5 关键CTQ (地板 Tai)", "en_US": "Top 5 Key CTQ (Floor Tai)"},

# ── common (shared across many views) ──────────────────────────
"common.delete_selected": {"zh_CN": "🗑 删除选中", "en_US": "🗑 Delete Selected"},
"common.import_done":     {"zh_CN": "导入完成", "en_US": "Import complete"},
"common.csv_filter":      {"zh_CN": "CSV文件 (*.csv)", "en_US": "CSV Files (*.csv)"},
"common.select_first":    {"zh_CN": "请先选择一条记录", "en_US": "Please select a record first"},

# ── voc_view.py ──────────────────────────────────────────────────
"voc.download_template":  {"zh_CN": "📄 下载导入模板", "en_US": "📄 Download Template"},
"voc.col_name":           {"zh_CN": "需求名称", "en_US": "Name"},
"voc.col_importance":     {"zh_CN": "重要度", "en_US": "Importance"},
"voc.col_kano":           {"zh_CN": "Kano类型", "en_US": "Kano Type"},
"voc.col_source":         {"zh_CN": "来源", "en_US": "Source"},
"voc.col_sales_point":    {"zh_CN": "销售点", "en_US": "Sales Point"},
"voc.col_ui":             {"zh_CN": "当前Ui", "en_US": "Current Ui"},
"voc.col_ti":             {"zh_CN": "计划Ti", "en_US": "Planned Ti"},
"voc.name_placeholder":   {"zh_CN": "输入需求名称", "en_US": "Enter VOC name"},
"voc.desc_placeholder":   {"zh_CN": "需求描述...", "en_US": "VOC description..."},
"voc.importance_tooltip": {"zh_CN": "支持2位小数，便于与AHP计算出的相对权重（×10缩放后）精确对应。",
                           "en_US": "Supports 2 decimal places, to precisely match AHP-computed relative weights (×10 scaled)."},
"voc.sales_point_tooltip": {"zh_CN": "销售点权重：1.0=一般, 1.2=重要, 1.5=非常重要", "en_US": "Sales point weight: 1.0=Normal, 1.2=Important, 1.5=Very important"},
"voc.ui_tooltip":         {"zh_CN": "当前满意水平 Ui：与「竞争基准 CBA」中我方产品的评分、以及「质量屋 HOQ」右墙的 Ui 列保持同步。",
                           "en_US": "Current satisfaction Ui: kept in sync with Our Product's score in Competition (CBA) and the HOQ right-wall Ui column."},
"voc.ui_label":           {"zh_CN": "当前水平 Ui:", "en_US": "Current Level Ui:"},
"voc.ti_label":           {"zh_CN": "计划水平 Ti:", "en_US": "Planned Level Ti:"},
"voc.ri_tooltip":         {"zh_CN": "改进比 Ri = 计划水平Ti / 当前水平Ui，自动计算，无需手动录入。", "en_US": "Improvement Ratio Ri = Planned Ti / Current Ui, computed automatically."},
"voc.ri_label_text":      {"zh_CN": "改进比 Ri (自动):", "en_US": "Improvement Ratio Ri (auto):"},
"voc.ri_needs_ui":        {"zh_CN": "- (需先设置Ui)", "en_US": "- (set Ui first)"},
"voc.adj_weight_full":    {"zh_CN": "调整后权重 Wai (Ri×Si×Ii): {v}", "en_US": "Adjusted Weight Wai (Ri×Si×Ii): {v}"},
"voc.select_first":       {"zh_CN": "请先选择一条需求", "en_US": "Please select a VOC item first"},
"voc.new_item_name":      {"zh_CN": "新需求", "en_US": "New VOC"},
"voc.select_parent_first": {"zh_CN": "请先选择一个父需求", "en_US": "Please select a parent VOC first"},
"voc.limit_title":        {"zh_CN": "限制", "en_US": "Limit"},
"voc.max_nesting":        {"zh_CN": "最多支持三级嵌套", "en_US": "Maximum 3 levels of nesting supported"},
"voc.new_child_name":     {"zh_CN": "新子需求", "en_US": "New Child VOC"},
"voc.confirm_delete_body": {"zh_CN": "确定删除需求「{name}」及其所有子需求？", "en_US": "Delete VOC \"{name}\" and all its children?"},
"voc.import_title":       {"zh_CN": "导入VOC数据", "en_US": "Import VOC Data"},
"voc.import_filter":      {"zh_CN": "CSV文件 (*.csv);;Excel文件 (*.xlsx);;所有文件 (*)", "en_US": "CSV Files (*.csv);;Excel Files (*.xlsx);;All Files (*)"},
"voc.download_template_title": {"zh_CN": "下载VOC导入模板", "en_US": "Download VOC Import Template"},
"voc.template_filename":  {"zh_CN": "VOC_导入模板.csv", "en_US": "VOC_Import_Template.csv"},
"voc.tpl_name":           {"zh_CN": "需求名称", "en_US": "name"},
"voc.tpl_desc":           {"zh_CN": "描述", "en_US": "description"},
"voc.tpl_source":         {"zh_CN": "来源", "en_US": "source"},
"voc.tpl_importance":     {"zh_CN": "重要度", "en_US": "importance"},
"voc.tpl_kano":           {"zh_CN": "Kano", "en_US": "kano"},
"voc.tpl_sales_point":    {"zh_CN": "销售点", "en_US": "sales_point"},
"voc.tpl_ui":             {"zh_CN": "当前水平", "en_US": "current_level"},
"voc.tpl_ti":             {"zh_CN": "计划水平", "en_US": "planned_level"},
"voc.template_saved_body": {"zh_CN": "模板已保存到:\n{path}\n\n说明：需求名称必填，其余列可留空；Kano填 M/O/A/I/R。\n「当前水平」会与竞争基准(CBA)中我方产品评分、质量屋(HOQ)的Ui列自动同步。",
                           "en_US": "Template saved to:\n{path}\n\nNote: Name is required, other columns may be left blank; Kano accepts M/O/A/I/R.\n\"Current Level\" auto-syncs with Our Product's score in Competition (CBA) and the HOQ Ui column."},

# ── FMEA view ─────────────────────────────────────────────────
"fmea.title":             {"zh_CN": "FMEA 失效模式与影响分析", "en_US": "FMEA - Failure Mode and Effects Analysis"},
"fmea.col_item":          {"zh_CN": "项目/功能", "en_US": "Item/Function"},
"fmea.col_failure_mode":  {"zh_CN": "潜在失效模式", "en_US": "Potential Failure Mode"},
"fmea.col_failure_effect": {"zh_CN": "潜在失效后果", "en_US": "Potential Effect"},
"fmea.col_severity":      {"zh_CN": "严重度\nS(1-10)", "en_US": "Severity\nS(1-10)"},
"fmea.col_failure_cause": {"zh_CN": "潜在失效原因", "en_US": "Potential Cause"},
"fmea.col_occurrence":    {"zh_CN": "发生度\nO(1-10)", "en_US": "Occurrence\nO(1-10)"},
"fmea.col_control":       {"zh_CN": "现有控制措施", "en_US": "Current Controls"},
"fmea.col_detection":     {"zh_CN": "探测度\nD(1-10)", "en_US": "Detection\nD(1-10)"},
"fmea.col_rpn":           {"zh_CN": "RPN", "en_US": "RPN"},
"fmea.col_risk_level":    {"zh_CN": "风险等级", "en_US": "Risk Level"},
"fmea.col_suggested":     {"zh_CN": "建议措施", "en_US": "Recommended Action"},
"fmea.col_responsible":   {"zh_CN": "责任人/日期", "en_US": "Responsible/Date"},
"fmea.type_dfmea":        {"zh_CN": "DFMEA (设计)", "en_US": "DFMEA (Design)"},
"fmea.type_pfmea":        {"zh_CN": "PFMEA (工艺)", "en_US": "PFMEA (Process)"},
"fmea.add_row":           {"zh_CN": "+ 添加行", "en_US": "+ Add Row"},
"fmea.import_hoq":        {"zh_CN": "📥 从HOQ导入CTQ", "en_US": "📥 Import CTQ from HOQ"},
"fmea.delete_row":        {"zh_CN": "🗑 删除选中行", "en_US": "🗑 Delete Selected Row"},
"fmea.export_csv":        {"zh_CN": "📤 导出CSV", "en_US": "📤 Export CSV"},
"fmea.hint":              {"zh_CN": "💡 RPN = 严重度(S) × 发生度(O) × 探测度(D)  |  红色: RPN≥200  橙色: RPN≥100  黄色: RPN≥50",
                           "en_US": "💡 RPN = Severity(S) × Occurrence(O) × Detection(D)  |  Red: RPN≥200  Orange: RPN≥100  Yellow: RPN≥50"},
"fmea.risk_high":         {"zh_CN": "高风险", "en_US": "High Risk"},
"fmea.risk_mid":          {"zh_CN": "中风险", "en_US": "Medium Risk"},
"fmea.risk_low":          {"zh_CN": "低风险", "en_US": "Low Risk"},
"fmea.risk_ok":           {"zh_CN": "可接受", "en_US": "Acceptable"},
"fmea.summary":           {"zh_CN": "📊 共 {total} 项  |  🔴 高风险(≥200): {high}  |  🟠 中风险(≥100): {mid}  |  🟡 低风险(≥50): {low}  |  🟢 可接受(<50): {ok}",
                           "en_US": "📊 {total} items  |  🔴 High(≥200): {high}  |  🟠 Medium(≥100): {mid}  |  🟡 Low(≥50): {low}  |  🟢 Acceptable(<50): {ok}"},
"fmea.need_project":      {"zh_CN": "请先打开一个项目", "en_US": "Please open a project first"},
"fmea.need_ctq":          {"zh_CN": "当前项目没有CTQ数据", "en_US": "This project has no CTQ data"},
"fmea.import_cause":      {"zh_CN": "重要度排名: #{rank}", "en_US": "Importance rank: #{rank}"},
"fmea.import_done_title": {"zh_CN": "导入完成", "en_US": "Import Complete"},
"fmea.import_done_body":  {"zh_CN": "已导入 {n} 个CTQ作为FMEA分析项", "en_US": "Imported {n} CTQs as FMEA analysis items"},
"fmea.dlg_export_title":  {"zh_CN": "导出FMEA", "en_US": "Export FMEA"},
"fmea.export_success":    {"zh_CN": "FMEA报告已导出: {path}", "en_US": "FMEA report exported: {path}"},

# ── DOE view ──────────────────────────────────────────────────
"doe.title":              {"zh_CN": "DOE 试验设计", "en_US": "DOE - Design of Experiments"},
"doe.hint":               {"zh_CN": "💡 定义因子及水平，自动生成全因子试验方案表。支持2-5个因子，每因子2-5个水平。",
                           "en_US": "💡 Define factors and levels to auto-generate a full factorial experiment table. Supports 2-5 factors, 2-5 levels each."},
"doe.factor_group":       {"zh_CN": "因子定义", "en_US": "Factor Definition"},
"doe.factor_name_placeholder": {"zh_CN": "因子名称 (如: 温度)", "en_US": "Factor name (e.g. Temperature)"},
"doe.factor_levels_placeholder": {"zh_CN": "水平值，逗号分隔 (如: 60,80,100)", "en_US": "Level values, comma-separated (e.g. 60,80,100)"},
"doe.add_factor":         {"zh_CN": "+ 添加因子", "en_US": "+ Add Factor"},
"doe.col_factor_name":    {"zh_CN": "因子名称", "en_US": "Factor Name"},
"doe.col_level_count":    {"zh_CN": "水平数", "en_US": "Level Count"},
"doe.col_level_values":   {"zh_CN": "水平值", "en_US": "Level Values"},
"doe.delete_factor":      {"zh_CN": "🗑 删除选中因子", "en_US": "🗑 Delete Selected Factor"},
"doe.generate":           {"zh_CN": "📊 生成试验方案", "en_US": "📊 Generate Design"},
"doe.design_type_group":  {"zh_CN": "设计类型", "en_US": "Design Type"},
"doe.full_factorial":     {"zh_CN": "全因子设计 (Full Factorial)", "en_US": "Full Factorial"},
"doe.l8_orthogonal":      {"zh_CN": "部分因子设计 (L8正交表)", "en_US": "Fractional Factorial (L8 Orthogonal Array)"},
"doe.run_count":          {"zh_CN": "试验次数: {n}", "en_US": "Runs: {n}"},
"doe.exp_table_title":    {"zh_CN": "试验方案表", "en_US": "Experiment Design Table"},
"doe.export_csv":         {"zh_CN": "📤 导出CSV", "en_US": "📤 Export CSV"},
"doe.need_name_and_levels": {"zh_CN": "请输入因子名称和水平值", "en_US": "Please enter a factor name and level values"},
"doe.need_2_levels":      {"zh_CN": "每个因子至少需要2个水平", "en_US": "Each factor needs at least 2 levels"},
"doe.max_5_factors":      {"zh_CN": "最多支持5个因子", "en_US": "Maximum 5 factors supported"},
"doe.need_factors":       {"zh_CN": "请先添加因子", "en_US": "Please add factors first"},
"doe.col_run_no":         {"zh_CN": "运行号", "en_US": "Run No."},
"doe.col_response":       {"zh_CN": "响应值(Y)", "en_US": "Response (Y)"},
"doe.col_remarks":        {"zh_CN": "备注", "en_US": "Remarks"},
"doe.full_factorial_result": {"zh_CN": "全因子设计: {n} 次试验", "en_US": "Full Factorial: {n} runs"},
"doe.l8_result":          {"zh_CN": "L8正交表: 8 次试验 ({n} 因子)", "en_US": "L8 Orthogonal Array: 8 runs ({n} factors)"},
"doe.need_design_first":  {"zh_CN": "请先生成试验方案", "en_US": "Please generate a design first"},
"doe.dlg_export_title":   {"zh_CN": "导出DOE方案", "en_US": "Export DOE Design"},
"doe.export_success":     {"zh_CN": "DOE方案已导出: {path}", "en_US": "DOE design exported: {path}"},

# ── DSM view ──────────────────────────────────────────────────
"dsm.title":              {"zh_CN": "DSM 设计结构矩阵", "en_US": "DSM - Design Structure Matrix"},
"dsm.add_element":        {"zh_CN": "+ 添加元素", "en_US": "+ Add Element"},
"dsm.import_ctq":         {"zh_CN": "📥 从CTQ导入", "en_US": "📥 Import from CTQ"},
"dsm.delete_last":        {"zh_CN": "🗑 删除最后一个", "en_US": "🗑 Delete Last"},
"dsm.clear_matrix":       {"zh_CN": "🧹 清空矩阵", "en_US": "🧹 Clear Matrix"},
"dsm.export_csv":         {"zh_CN": "📤 导出CSV", "en_US": "📤 Export CSV"},
"dsm.hint":               {"zh_CN": "💡 点击矩阵单元格标记依赖关系: 空→X(依赖)→空  |  对角线为元素自身(灰色)",
                           "en_US": "💡 Click cells to mark dependencies: ∅→X(depends)→?(uncertain)→∅  |  Diagonal is the element itself (gray)"},
"dsm.analysis_group":     {"zh_CN": "结构分析", "en_US": "Structure Analysis"},
"dsm.analyze":            {"zh_CN": "📊 分析依赖结构", "en_US": "📊 Analyze Dependencies"},
"dsm.add_element_title":  {"zh_CN": "添加元素", "en_US": "Add Element"},
"dsm.add_element_label":  {"zh_CN": "元素名称:", "en_US": "Element Name:"},
"dsm.need_project":       {"zh_CN": "请先打开一个项目", "en_US": "Please open a project first"},
"dsm.need_ctq":           {"zh_CN": "当前项目没有CTQ数据", "en_US": "This project has no CTQ data"},
"dsm.import_done_title":  {"zh_CN": "导入完成", "en_US": "Import Complete"},
"dsm.import_done_body":   {"zh_CN": "已导入 {n} 个CTQ作为DSM元素", "en_US": "Imported {n} CTQs as DSM elements"},
"dsm.need_elements":      {"zh_CN": "请先添加元素", "en_US": "Please add elements first"},
"dsm.analysis_size":      {"zh_CN": "<b>矩阵规模:</b> {n}×{n}  |  ", "en_US": "<b>Matrix size:</b> {n}×{n}  |  "},
"dsm.analysis_total":     {"zh_CN": "<b>总依赖数:</b> {n}  |  ", "en_US": "<b>Total dependencies:</b> {n}  |  "},
"dsm.analysis_density":   {"zh_CN": "<b>密度:</b> {pct}%<br/><br/>", "en_US": "<b>Density:</b> {pct}%<br/><br/>"},
"dsm.analysis_most_out":  {"zh_CN": "<b>最多输出依赖:</b> {name} ({n}个)<br/>", "en_US": "<b>Most outgoing dependencies:</b> {name} ({n})<br/>"},
"dsm.analysis_most_in":   {"zh_CN": "<b>最多被依赖:</b> {name} ({n}个)<br/>", "en_US": "<b>Most depended-on:</b> {name} ({n})<br/>"},
"dsm.analysis_clusters":  {"zh_CN": "<br/><b>🔄 双向依赖(耦合):</b> {list}<br/>", "en_US": "<br/><b>🔄 Bidirectional (coupled):</b> {list}<br/>"},
"dsm.analysis_clusters_note": {"zh_CN": "耦合元素需要迭代设计，建议集中在同一团队处理。", "en_US": "Coupled elements require iterative design — consider assigning them to the same team."},
"dsm.analysis_independent": {"zh_CN": "<br/><b>独立元素:</b> {list}<br/>", "en_US": "<br/><b>Independent elements:</b> {list}<br/>"},
"dsm.analysis_independent_note": {"zh_CN": "独立元素可以并行开发。", "en_US": "Independent elements can be developed in parallel."},
"dsm.dlg_export_title":   {"zh_CN": "导出DSM", "en_US": "Export DSM"},
"dsm.export_success":     {"zh_CN": "DSM矩阵已导出: {path}", "en_US": "DSM matrix exported: {path}"},

# ── Welcome poster ────────────────────────────────────────────
"welcome.node_kano":      {"zh_CN": "需求分类", "en_US": "Classification"},
"welcome.node_ahp":       {"zh_CN": "权重分析", "en_US": "Weighting"},
"welcome.node_triz":      {"zh_CN": "矛盾矩阵", "en_US": "Contradiction Matrix"},
"welcome.node_pareto":    {"zh_CN": "优先级排序", "en_US": "Prioritization"},
"welcome.node_fmea":      {"zh_CN": "风险分析", "en_US": "Risk Analysis"},
"welcome.node_doe":       {"zh_CN": "试验设计", "en_US": "Experiment Design"},
"welcome.node_dsm":       {"zh_CN": "结构矩阵", "en_US": "Structure Matrix"},
"welcome.hoq_badge":      {"zh_CN": "HOQ 质量屋", "en_US": "HOQ"},
"welcome.title":          {"zh_CN": "OpenQFD — 质量功能展开软件", "en_US": "OpenQFD — Quality Function Deployment"},
"welcome.subtitle":       {"zh_CN": "从顾客之声到工程决策 — VOC · CTQ · HOQ · KANO · AHP · Pareto · TRIZ · FMEA · DOE · DSM 十大质量工具一体化平台",
                           "en_US": "From Voice of Customer to Engineering Decisions — an integrated platform of 10 quality tools: VOC · CTQ · HOQ · KANO · AHP · Pareto · TRIZ · FMEA · DOE · DSM"},
"welcome.hint":           {"zh_CN": "💡 从上方「文件」菜单开始：新建项目 / 新建示例项目 / 导入JSON项目 / 打开已有项目",
                           "en_US": "💡 Start from the File menu above: New Project / New Sample Project / Import JSON / Open Existing Project"},

# ── TRIZ view ─────────────────────────────────────────────────
"triz.title":             {"zh_CN": "TRIZ 发明问题解决理论", "en_US": "TRIZ - Theory of Inventive Problem Solving"},
"triz.tab_matrix":        {"zh_CN": "🔀 矛盾矩阵", "en_US": "🔀 Contradiction Matrix"},
"triz.tab_principles":    {"zh_CN": "💡 40条发明原理", "en_US": "💡 40 Inventive Principles"},
"triz.matrix_hint":       {"zh_CN": "💡 选择要改善的参数和恶化的参数，查看推荐的发明原理", "en_US": "💡 Select the parameter to improve and the one that worsens, to see recommended principles"},
"triz.improving_param":   {"zh_CN": "要改善的参数:", "en_US": "Improving Parameter:"},
"triz.worsening_param":   {"zh_CN": "恶化的参数:", "en_US": "Worsening Parameter:"},
"triz.lookup":            {"zh_CN": "🔍 查找原理", "en_US": "🔍 Look Up Principles"},
"triz.same_param_error":  {"zh_CN": "改善参数和恶化参数不能相同", "en_US": "The improving and worsening parameters cannot be the same"},
"triz.result_header":     {"zh_CN": "改善「{improving}」同时避免「{worsening}」恶化", "en_US": "Improve \"{improving}\" while avoiding worsening \"{worsening}\""},
"triz.recommended":       {"zh_CN": "推荐发明原理：", "en_US": "Recommended Inventive Principles:"},
"triz.no_recommendation": {"zh_CN": "该组合暂无推荐原理。请尝试其他参数组合，或浏览40条发明原理寻找灵感。",
                           "en_US": "No recommendation for this combination. Try other parameters, or browse the 40 principles for inspiration."},
"help.contact_line":      {"zh_CN": "OpenQFD V{version} — 微信公众号「OpenQuality」", "en_US": "OpenQFD V{version} — WeChat: \"OpenQuality\""},

# ── License agreement ──────────────────────────────────────────
"menu.view_license":      {"zh_CN": "查看许可协议...", "en_US": "View License Agreement..."},
"lic.view_license_title": {"zh_CN": "许可协议", "en_US": "License Agreement"},
"lic.load_failed":        {"zh_CN": "无法加载许可协议文件 (LICENSE.md)。", "en_US": "Could not load the license file (LICENSE.md)."},
"gate.title":             {"zh_CN": "欢迎使用 OpenQFD", "en_US": "Welcome to OpenQFD"},
"gate.heading":           {"zh_CN": "OpenQFD — 质量功能展开软件", "en_US": "OpenQFD — Quality Function Deployment"},
"gate.summary":           {"zh_CN": "本软件基于 PolyForm Noncommercial License 1.0.0 协议发布：\n"
                                     "• 个人 / 非商业用途完全免费；\n"
                                     "• 企业或商业用途须购买官方商业授权后方可使用；\n"
                                     "• 未经授权用于商业用途，OpenQFD 官方将保留追究法律责任的权利。\n\n"
                                     "点击下方按钮查看完整协议全文。",
                           "en_US": "This software is released under the PolyForm Noncommercial License 1.0.0:\n"
                                     "• Free for personal / noncommercial use;\n"
                                     "• Commercial or business use requires purchasing an official commercial license;\n"
                                     "• Unauthorized commercial use may result in legal action.\n\n"
                                     "Click the button below to read the full agreement."},
"gate.view_full":         {"zh_CN": "📄 查看完整协议", "en_US": "📄 View Full Agreement"},
"gate.agree_checkbox":    {"zh_CN": "我已阅读并同意《OpenQFD 使用许可协议》", "en_US": "I have read and agree to the OpenQFD License Agreement"},
"gate.wechat_box":        {"zh_CN": "💡 关注微信公众号「<b>OpenQuality</b>」，回复 <b>QFD授权码</b> 即可领取 OpenQFD 授权码，解锁全部功能。",
                           "en_US": "💡 Follow the WeChat official account \"<b>OpenQuality</b>\" and reply <b>QFD授权码</b> to get a free OpenQFD license key unlocking all features."},
"gate.enter":             {"zh_CN": "✅ 同意协议并进入软件", "en_US": "✅ Agree && Enter OpenQFD"},
"gate.exit":              {"zh_CN": "退出", "en_US": "Exit"},
"gate.choose_language":   {"zh_CN": "选择语言", "en_US": "Choose your language"},
"gate.agree_prefix":      {"zh_CN": "我已阅读并同意", "en_US": "I agree to the"},
"gate.agree_link":        {"zh_CN": "《许可协议》", "en_US": "License Agreement"},
"gate.details_title":     {"zh_CN": "许可协议与授权说明", "en_US": "License & Activation Info"},
"lic.locked_status":      {"zh_CN": "「{name}」为授权版功能，请输入授权码激活", "en_US": "\"{name}\" is a licensed feature — please enter a license key to activate"},
"lic.purchase_info":      {"zh_CN": "💬 授权版：关注微信公众号「OpenQuality」自动获取授权码，解锁所有功能。\n☎️ 商业版：商用许可、售后或定制，请联系021-58108606。",
                           "en_US": "💬 Licensed: Follow the WeChat account \"OpenQuality\" to automatically get a license key and unlock all features.\n☎️ Commercial: For commercial licensing, after-sales support, or customization, contact 021-58108606."},
}


# ══════════════════════════════════════════════════════════════
#  Public API
# ══════════════════════════════════════════════════════════════

def t(key: str, **kwargs) -> str:
    """Translate a key to the current language."""
    entry = _DICT.get(key)
    if not entry:
        return key
    text = entry.get(_current_lang, entry.get("zh_CN", key))
    if kwargs:
        text = text.format(**kwargs)
    return text


def set_language(lang: str):
    """Set the current language. Supported: zh_CN, en_US."""
    global _current_lang
    if lang in LANGS:
        _current_lang = lang
        _save_lang_pref(lang)


def get_language() -> str:
    return _current_lang


def toggle_language() -> str:
    """Toggle between zh_CN and en_US. Returns new language."""
    new = "en_US" if _current_lang == "zh_CN" else "zh_CN"
    set_language(new)
    return new


def _save_lang_pref(lang):
    """Persist language preference."""
    try:
        pref_dir = Path.home() / ('.config' if os.name != 'nt' else '')
        if os.name == 'nt':
            pref_dir = Path(os.environ.get('APPDATA', Path.home()))
        pref_dir = pref_dir / 'OpenQFD'
        pref_dir.mkdir(parents=True, exist_ok=True)
        with open(pref_dir / 'lang.json', 'w') as f:
            json.dump({"lang": lang}, f)
    except Exception:
        pass


def load_lang_pref():
    """Load saved language preference on startup."""
    global _current_lang
    try:
        pref_dir = Path.home() / ('.config' if os.name != 'nt' else '')
        if os.name == 'nt':
            pref_dir = Path(os.environ.get('APPDATA', Path.home()))
        pref_dir = pref_dir / 'OpenQFD'
        pref_file = pref_dir / 'lang.json'
        if pref_file.exists():
            with open(pref_file, 'r') as f:
                data = json.load(f)
            lang = data.get("lang", "zh_CN")
            if lang in LANGS:
                _current_lang = lang
    except Exception:
        pass


# Load on import
load_lang_pref()
