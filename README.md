# OpenQFD — 质量功能展开软件 V3.0

<p align="center">
  <img src="assets/logo.png" width="128" alt="OpenQFD Logo"><br>
  <b>Quality Function Deployment</b> — 将顾客之声系统转化为设计参数<br>
  基于 PySide6 的桌面端 QFD 分析平台，集成 TRIZ / FMEA / DOE / DSM 质量工具<br>
  支持中文 / English 双语界面
</p>

---

## 下载

当前版本 **v2026.08.01**。免安装 Python 环境的预编译一键运行包（Windows / macOS / Linux）请前往：

**[GitHub Releases](https://github.com/OpenQuality/OpenQFD/releases/latest)**

| 平台 | 文件 | 运行方式 |
|---|---|---|
| Windows | `OpenQFD-windows.zip` | 解压后双击 `OpenQFD.exe` |
| macOS | `OpenQFD-macos.zip` | 解压后双击 `OpenQFD.app`（首次打开需在「系统设置 → 隐私与安全性」允许） |
| Linux | `OpenQFD-linux.zip` | 解压后 `chmod +x OpenQFD && ./OpenQFD` |

不想用预编译包，或想直接跑源码，见下方「快速开始」。

---

## V3.0 新特性

- 🏷️ **三级版本体系**：免费版 / 授权版（关注公众号免费获取）/ 商业版（付费购买，含商用许可与售后），授权管理页面按版本分别展示状态和购买信息
- ⚡ **切换语言 / 授权状态无需重启**：改为进程内直接刷新界面，避免打包为 exe 后偶发的重启崩溃问题
- 🎨 **侧栏语言切换按钮**：中/EN 分段式控件，当前语言高亮显示，替代原先的单按钮切换
- 🏷️ **英文模块名称调整**：Voice of Customer (VOC)、Critical To Quality (CTQ)、Competition Benchmarking Analysis (CBA)
- 📦 **打包体积优化**：排除未使用的 Qt QML/Quick/Pdf 模块及 lxml，独立 exe 体积精简约5MB
- 🐛 修复项目总览页「快速操作」冗余区块、多处授权/购买文案表述

## V2.0 新特性

- 🌐 **中英文双语界面**：侧栏一键切换 简体中文 / English，全部模块、菜单、导出内容同步翻译
- 📜 **软件许可协议**：采用 PolyForm Noncommercial License 1.0.0，个人/非商业用途免费，商业用途需购买授权（详见 [LICENSE.md](LICENSE.md)）
- 🚪 **首次启动引导页**：首次打开需选择界面语言并同意许可协议，简洁版 PyCharm 风格设置向导
- 🔄 **项目管理增强**：自动记住并加载上次项目、菜单内「切换项目」快捷列表、多个示例项目自动编号
- 🖼️ **首页海报**：使用真实示例项目数据渲染质量屋预览图，替换原先的示意图
- 🐛 多项界面细节修复：数据切换后残留旧图表、质量屋在零 CTQ 时崩溃、授权激活后无法打开授权管理等

---

## 版本说明

| | 免费版 | 授权版 |
|---|---|---|
| VOC 顾客需求管理 | ✅ | ✅ |
| CTQ 技术需求管理 | ✅ | ✅ |
| **质量屋 HOQ (一体化七区)** | ✅ | ✅ |
| 项目管理 / 示例项目 | ✅ | ✅ |
| PNG 图片导出 | ✅ | ✅ |
| **竞争基准分析 (雷达图/柱状图)** | ✅ | ✅ |
| Kano 需求分类 | 🔒 | ✅ |
| AHP 层次分析法 | 🔒 | ✅ |
| Pareto 优先级分析 | 🔒 | ✅ |
| 四阶段 QFD 级联展开 | 🔒 | ✅ |
| **TRIZ 发明原理 + 矛盾矩阵** | 🔒 | ✅ |
| **FMEA 失效模式分析 (RPN)** | 🔒 | ✅ |
| **DOE 试验设计 (全因子/正交表)** | 🔒 | ✅ |
| **DSM 设计结构矩阵** | 🔒 | ✅ |
| 完整导出 (Excel/CSV/JSON) | 🔒 | ✅ |
| 版本控制 (快照/回滚) | 🔒 | ✅ |

获取授权码请打开软件内「授权 → 授权管理」页面查看联系方式（授权版关注微信公众号「OpenQuality」免费领取；商业版请联系 021-58108606）。

---

## 快速开始

### 自动部署（推荐）

**Windows:**
```
1. 解压 OpenQFD.zip
2. 右键 setup_windows.ps1 → 使用 PowerShell 运行
3. 双击桌面「OpenQFD」图标启动
```

**Linux / macOS:**
```bash
unzip OpenQFD.zip && cd OpenQFD
chmod +x setup_unix.sh && ./setup_unix.sh
./qfd.sh
```

### 手动部署

```bash
cd OpenQFD
python -m venv .venv
# Windows:    .venv\Scripts\Activate.ps1
# Linux/Mac:  source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

> 详细部署/卸载说明见 [DEPLOY.md](DEPLOY.md)

---

## 功能一览

### 质量屋 HOQ（一体化七区视图）
屋顶(相关矩阵) + 天花板(CTQ) + 左墙(VOC) + 房间(关系矩阵) + 右墙(竞争评估) + 地板(技术重要度) + 地下室(竞品基准)

### VOC / CTQ 管理
三级树状嵌套、Excel/CSV导入、Kano分类、重要度评分

### 高级分析（授权版）
- **竞争基准**: 雷达图 + 柱状对比
- **Kano**: 五类分类、象限图、自动建议
- **AHP**: 成对比较 + 一致性检验 (CR<0.1)
- **Pareto**: 柱状图 + 累计曲线 + 二八法则

### TRIZ 发明原理（授权版）
- 40条发明原理浏览器（中英双语）
- 39个工程参数矛盾矩阵查询
- 选择"改善参数"和"恶化参数"自动推荐发明原理

### FMEA 失效分析（授权版）
- DFMEA / PFMEA 工作表
- S×O×D 自动计算 RPN 值
- 风险等级色标: 红(≥200) / 橙(≥100) / 黄(≥50) / 绿(<50)
- 从 HOQ 一键导入高优先级 CTQ
- CSV 导出 FMEA 报告

### DOE 试验设计（授权版）
- 因子定义 (2-5因子，每因子2-5水平)
- 全因子设计自动生成
- L8正交表 (部分因子设计)
- 试验方案表 CSV 导出

### DSM 设计结构矩阵（授权版）
- N×N 依赖关系矩阵 (点击标记 X 依赖)
- 从 CTQ 一键导入元素
- 结构分析: 耦合检测、独立元素识别、密度统计
- CSV 矩阵导出

### 四阶段展开（授权版）
产品规划 → 零件展开 → 工艺规划 → 生产控制，一键级联

### 导出与版本
Excel多Sheet、PNG/SVG、FMEA CSV、JSON备份、版本快照回滚

---

## 授权管理

### 在线云端验证
采用腾讯云函数在线验证，激活后支持 30 天离线使用。
**一码一机**——授权码激活时绑定当前设备，如需更换设备，请先在旧设备「取消激活」后再到新设备激活。

### 激活步骤
1. 点击菜单栏 **授权 → 授权管理...**
2. 输入授权码 `OQFD-XXXX-XXXX-XXXX-XXXX`
3. 点击激活，确认重启即可

---

## 项目结构

```
OpenQFD/
├── main.py                     # 主程序入口
├── LICENSE.md                  # 软件许可协议全文
├── requirements.txt            # Python 依赖
├── setup_windows.ps1           # Windows 自动部署
├── setup_unix.sh               # Linux/macOS 自动部署
├── build_installer.py          # PyInstaller 打包
├── assets/                     # 图标和Logo
├── models/
│   ├── database.py             # SQLite 数据层
│   ├── license.py              # 云端授权客户端
│   └── settings.py             # 本地设置持久化（语言/上次项目等）
├── engines/
│   └── compute.py              # HOQ / AHP / Kano 引擎
├── views/
│   ├── hoq_view.py             # 质量屋一体化视图
│   ├── voc_view.py / ctq_view.py
│   ├── competition_view.py     # 竞争分析
│   ├── analysis_views.py       # AHP / Kano / Pareto
│   ├── phase_view.py           # 四阶段展开
│   ├── triz_view.py            # TRIZ 发明原理
│   ├── fmea_view.py            # FMEA 失效分析
│   ├── doe_view.py             # DOE 试验设计
│   ├── dsm_view.py             # DSM 结构矩阵
│   ├── export_view.py          # 导出和版本
│   ├── help_view.py            # 帮助手册
│   ├── welcome_view.py         # 首页欢迎海报
│   └── styles.py               # UI 样式
└── utils/
    ├── fonts.py                # 中文字体配置
    └── i18n.py                 # 国际化 (中/英)
```

---

© 2026 OpenQuality · 微信公众号「OpenQuality」
