"""
QFD Software - Main Application Window
Central hub connecting all modules: VOC, CTQ, HOQ, Competition, AHP, Kano, Pareto, Phases, Export.
"""
import sys
import os

# MUST be before any local imports - add project root to Python path
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
if _APP_DIR not in sys.path:
    sys.path.insert(0, _APP_DIR)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QListWidget, QListWidgetItem, QPushButton,
    QLabel, QDialog, QDialogButtonBox, QLineEdit, QTextEdit,
    QComboBox, QFormLayout, QGroupBox, QMessageBox, QSplitter,
    QFrame, QFileDialog, QStatusBar, QScrollArea, QCheckBox, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, QTimer, QProcess
from PySide6.QtGui import QFont, QIcon, QColor, QGuiApplication, QPixmap, QPalette

from models.database import Database
from models.settings import load_settings, save_settings
from models.license import (
    load_license, activate_license, deactivate_license, remove_license,
    validate_license_format, check_server_status, get_machine_id,
    is_module_allowed, EDITION_FREE, EDITION_LICENSED, EDITION_COMMERCIAL,
    FREE_MODULES, COMMERCIAL_MODULES, PURCHASE_CONTACT,
    APP_VERSION, check_for_update,
)
from views.styles import build_main_stylesheet, SIDEBAR_STYLE, COLORS, INDUSTRIES, INDUSTRY_KEYS, PHASE_NAMES, KANO_TYPES, KANO_TYPE_KEYS
from views.voc_view import VOCManagerView
from views.ctq_view import CTQManagerView
from views.hoq_view import HOQMatrixView
from views.competition_view import CompetitionView
from views.analysis_views import AHPView, KanoView, ParetoView
from views.phase_view import PhaseView
from views.export_view import ExportView, VersionView
from views.help_view import HelpDialog
from views.triz_view import TRIZView
from views.fmea_view import FMEAView
from views.doe_view import DOEView
from views.dsm_view import DSMView
from views.welcome_view import WelcomeView
from engines.compute import HOQEngine
from utils.i18n import t, set_language, get_language, load_lang_pref


def restart_application():
    """Quit this process and relaunch a fresh instance (so a new license/edition takes effect).

    On a frozen (PyInstaller onefile) Windows build, the new instance is started only
    AFTER this process has fully exited: two instances of the same onefile exe share
    one deterministic extraction temp folder, so starting the new one while the old
    one is still exiting races on that folder and can crash with spurious
    "module partially initialized" / missing-file errors.
    """
    args = list(sys.argv[1:])
    if not getattr(sys, "frozen", False):
        args = [os.path.abspath(__file__)] + args

    if getattr(sys, "frozen", False) and os.name == 'nt':
        pid = os.getpid()
        exe = sys.executable.replace("'", "''")
        arg_list = ",".join(f"'{a}'" for a in args) if args else ""
        start_cmd = f"Start-Process -FilePath '{exe}'" + (f" -ArgumentList {arg_list}" if arg_list else "")
        watcher = f"Wait-Process -Id {pid} -ErrorAction SilentlyContinue; {start_cmd}"
        QProcess.startDetached("powershell", ["-NoProfile", "-WindowStyle", "Hidden", "-Command", watcher])
    else:
        QProcess.startDetached(sys.executable, args)
    QApplication.quit()


# Module gating: maps nav row → license module name
NAV_MODULE_MAP = {
    0: "project",       # Overview
    1: "voc",           # VOC
    2: "ctq",           # CTQ
    3: "competition",   # Competition (CBA) — before HOQ
    4: "hoq",           # HOQ
    5: "kano",          # Kano
    6: "ahp",           # AHP
    7: "pareto",        # Pareto
    8: "phase",         # 4-Phase
    9: "triz",          # TRIZ
    10: "fmea",         # FMEA
    11: "doe",          # DOE
    12: "dsm",          # DSM
    13: "export_full",  # Export
    14: "version",      # Version
}


class LicenseDialog(QDialog):
    """Dialog for cloud-based license activation / deactivation."""
    def __init__(self, current_license, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("lic.title"))
        self.setMinimumWidth(540)
        self._result_key = None
        layout = QVBoxLayout(self)

        # Current status
        status_group = QGroupBox(t("lic.current"))
        sg = QVBoxLayout(status_group)
        edition = current_license.get("edition", EDITION_FREE)
        key = current_license.get("key")
        online = current_license.get("online", False)
        grace = current_license.get("grace_days_remaining", 0)

        STATUS_STYLE = {
            EDITION_FREE:       ("lic.status_free",       "#E67E22"),
            EDITION_LICENSED:   ("lic.status_licensed",   "#27AE60"),
            EDITION_COMMERCIAL: ("lic.status_commercial", "#2980B9"),
        }
        status_key, status_color = STATUS_STYLE.get(edition, STATUS_STYLE[EDITION_FREE])
        status_lbl = QLabel(t(status_key, contact=PURCHASE_CONTACT))
        status_lbl.setWordWrap(True)
        status_lbl.setStyleSheet(f"color: {status_color}; font-size: 14px; font-weight: bold;")
        sg.addWidget(status_lbl)

        if edition in (EDITION_LICENSED, EDITION_COMMERCIAL):
            online_tag = t("lic.online_verified") if online else t("lic.offline_cache", grace=grace)
            key_lbl = QLabel(t("lic.key_line", lic_key=key, online_tag=online_tag))
            key_lbl.setStyleSheet("color: #7F8C8D; font-size: 12px;")
            sg.addWidget(key_lbl)
            btn_deactivate = QPushButton(t("lic.deactivate"))
            btn_deactivate.setObjectName("danger")
            btn_deactivate.clicked.connect(self._deactivate)
            sg.addWidget(btn_deactivate)
        layout.addWidget(status_group)

        # Activate
        activate_group = QGroupBox(t("lic.activate_section"))
        ag = QVBoxLayout(activate_group)
        ag.addWidget(QLabel(t("lic.enter_key")))
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("OQFD-XXXX-XXXX-XXXX-XXXX")
        self.key_input.setFont(QFont("Consolas", 14))
        self.key_input.setMinimumHeight(40)
        ag.addWidget(self.key_input)

        # Server status indicator
        self.server_status = QLabel(t("lic.checking_server"))
        self.server_status.setStyleSheet("color: #7F8C8D; font-size: 12px;")
        ag.addWidget(self.server_status)
        # Check server in background
        QTimer.singleShot(100, self._check_server)

        btn_activate = QPushButton(t("lic.activate"))
        btn_activate.setObjectName("success")
        btn_activate.setMinimumHeight(42)
        btn_activate.clicked.connect(self._activate)
        ag.addWidget(btn_activate)
        layout.addWidget(activate_group)

        # Purchase info
        info_group = QGroupBox(t("lic.purchase"))
        ig = QVBoxLayout(info_group)
        purchase_lbl = QLabel(t("lic.features_body", purchase_info=t("lic.purchase_info"), days=30))
        purchase_lbl.setWordWrap(True)
        purchase_lbl.setStyleSheet("font-size: 13px; line-height: 1.5;")
        purchase_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        ig.addWidget(purchase_lbl)
        layout.addWidget(info_group)

        btn_close = QPushButton(t("common.close"))
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def _check_server(self):
        """Check server connectivity."""
        if check_server_status():
            self.server_status.setText(t("lic.server_ok"))
            self.server_status.setStyleSheet("color: #27AE60; font-size: 12px;")
        else:
            self.server_status.setText(t("lic.server_fail"))
            self.server_status.setStyleSheet("color: #E74C3C; font-size: 12px;")

    def _activate(self):
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, t("common.hint"), t("lic.enter_key_warning"))
            return

        # Format pre-check
        if not validate_license_format(key):
            QMessageBox.warning(self, t("common.error"), t("lic.format_error", purchase_info=t("lic.purchase_info")))
            return

        # Online activation
        self.server_status.setText(t("lic.activating"))
        self.server_status.setStyleSheet("color: #2980B9; font-size: 12px;")
        self.repaint()  # Force UI update

        result = activate_license(key)

        if result.get("ok"):
            self._result_key = result.get("key")
            reply = QMessageBox.question(self, t("common.success"), t("lic.activated_msg"),
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            self.accept()
            if reply == QMessageBox.Yes:
                self._reload_or_restart()
        else:
            error_code = result.get("error", "")
            message = result.get("message", error_code)
            if error_code == "already_bound":
                self.server_status.setText(t("lic.already_bound_short"))
                self.server_status.setStyleSheet("color: #E74C3C; font-size: 12px;")
                QMessageBox.warning(self, t("common.error"), t("lic.already_bound_full", purchase_info=t("lic.purchase_info")))
            else:
                self.server_status.setText(f"❌ {message}")
                self.server_status.setStyleSheet("color: #E74C3C; font-size: 12px;")
                QMessageBox.critical(self, t("common.error"),
                    t("lic.activate_fail", message=message, purchase_info=t("lic.purchase_info")))

    def _deactivate(self):
        reply = QMessageBox.question(self, t("common.confirm"), t("lic.deactivate_confirm"))
        if reply == QMessageBox.Yes:
            deactivate_license()  # Cloud unbind + local cleanup
            reply2 = QMessageBox.question(self, t("common.success"), t("lic.deactivated_msg"),
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            self.accept()
            if reply2 == QMessageBox.Yes:
                self._reload_or_restart()

    def _reload_or_restart(self):
        """Prefer rebuilding the MainWindow in-place (no second OS process — see
        MainWindow._reload_ui). Only fall back to a real process restart if this
        dialog somehow wasn't opened with a MainWindow as its parent."""
        parent = self.parent()
        if parent is not None and hasattr(parent, "_reload_ui"):
            QTimer.singleShot(0, parent._reload_ui)
        else:
            restart_application()

    def get_result(self):
        return self._result_key


def _load_license_markdown():
    """Read LICENSE.md from the app directory. Returns None if unavailable."""
    try:
        with open(os.path.join(_APP_DIR, "LICENSE.md"), "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


class LicenseTextDialog(QDialog):
    """Shows the full LICENSE.md text (PolyForm Noncommercial + commercial addendum)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("lic.view_license_title"))
        self.setMinimumSize(720, 620)
        layout = QVBoxLayout(self)
        browser = QTextEdit()
        browser.setReadOnly(True)
        md = _load_license_markdown()
        if md:
            browser.setMarkdown(md)
        else:
            browser.setPlainText(t("lic.load_failed"))
        layout.addWidget(browser)
        btn_close = QPushButton(t("common.close"))
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)


class GateDetailsDialog(QDialog):
    """License summary + WeChat promo — tucked behind the startup gate's
    "License Agreement" link instead of being shown on the gate itself."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("gate.details_title"))
        self.setMinimumWidth(480)
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        summary = QLabel(t("gate.summary"))
        summary.setWordWrap(True)
        summary.setStyleSheet("font-size: 13px; color: #2C3E50;")
        layout.addWidget(summary)

        btn_view = QPushButton(t("gate.view_full"))
        btn_view.setObjectName("secondary")
        btn_view.clicked.connect(self._view_full)
        layout.addWidget(btn_view)

        wechat_box = QLabel(t("gate.wechat_box"))
        wechat_box.setWordWrap(True)
        wechat_box.setTextFormat(Qt.RichText)
        wechat_box.setStyleSheet("background:#FFF3E0; padding:12px; border-radius:8px; font-size:12px; color:#6D4C00;")
        layout.addWidget(wechat_box)

        btn_close = QPushButton(t("common.close"))
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def _view_full(self):
        dlg = LicenseTextDialog(self)
        dlg.exec()


class StartupGateDialog(QDialog):
    """First-run gate, styled like a minimal setup wizard (PyCharm-style):
    just the language choice and a single agreement checkbox. The license
    text and WeChat promo are tucked behind a "License Agreement" link
    instead of being shown directly."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("OpenQFD")
        self.setFixedSize(600, 460)
        self.setModal(True)
        self._lang = get_language()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(12, 10, 12, 0)
        top_row.addStretch()
        btn_exit = QPushButton("✕")
        btn_exit.setFixedSize(24, 24)
        btn_exit.setCursor(Qt.PointingHandCursor)
        btn_exit.setStyleSheet("""
            QPushButton { border: none; background: transparent; color: #95A5A6; font-size: 13px; }
            QPushButton:hover { color: #E74C3C; }
        """)
        btn_exit.clicked.connect(self._on_exit)
        top_row.addWidget(btn_exit)
        outer.addLayout(top_row)

        body = QVBoxLayout()
        body.setContentsMargins(70, 4, 70, 36)
        body.setSpacing(0)

        icon_path = os.path.join(_APP_DIR, "assets", "icon_64.png")
        if os.path.exists(icon_path):
            icon_lbl = QLabel()
            icon_lbl.setPixmap(QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            icon_lbl.setAlignment(Qt.AlignCenter)
            body.addWidget(icon_lbl)
            body.addSpacing(14)

        self.heading_lbl = QLabel("OpenQFD")
        self.heading_lbl.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        self.heading_lbl.setStyleSheet("color: #1B5E8C;")
        self.heading_lbl.setAlignment(Qt.AlignCenter)
        body.addWidget(self.heading_lbl)

        self.tagline_lbl = QLabel()
        self.tagline_lbl.setStyleSheet("color: #7F8C8D; font-size: 12px;")
        self.tagline_lbl.setAlignment(Qt.AlignCenter)
        body.addWidget(self.tagline_lbl)

        body.addSpacing(30)

        self.lang_lbl = QLabel()
        self.lang_lbl.setStyleSheet("color: #7F8C8D; font-size: 11px;")
        self.lang_lbl.setAlignment(Qt.AlignCenter)
        body.addWidget(self.lang_lbl)
        body.addSpacing(8)

        lang_row = QHBoxLayout()
        lang_row.setSpacing(10)
        lang_row.addStretch()
        self.btn_lang_zh = QPushButton("简体中文")
        self.btn_lang_en = QPushButton("English")
        for b in (self.btn_lang_zh, self.btn_lang_en):
            b.setFixedHeight(36)
            b.setMinimumWidth(140)
            b.setCursor(Qt.PointingHandCursor)
        self.btn_lang_zh.clicked.connect(lambda: self._select_lang("zh_CN"))
        self.btn_lang_en.clicked.connect(lambda: self._select_lang("en_US"))
        lang_row.addWidget(self.btn_lang_zh)
        lang_row.addWidget(self.btn_lang_en)
        lang_row.addStretch()
        body.addLayout(lang_row)

        body.addSpacing(34)

        agree_row = QHBoxLayout()
        agree_row.setSpacing(4)
        agree_row.addStretch()
        self.agree_check = QCheckBox()
        self.agree_check.setCursor(Qt.PointingHandCursor)
        self.agree_check.stateChanged.connect(self._on_check_changed)
        agree_row.addWidget(self.agree_check)
        self.agree_lbl = QLabel()
        self.agree_lbl.setStyleSheet("font-size: 12px; color: #2C3E50;")
        agree_row.addWidget(self.agree_lbl)
        self.agree_link_btn = QPushButton()
        self.agree_link_btn.setFlat(True)
        self.agree_link_btn.setCursor(Qt.PointingHandCursor)
        self.agree_link_btn.setStyleSheet("""
            QPushButton { border: none; background: transparent; color: #1B5E8C;
                          text-decoration: underline; font-size: 12px; padding: 0; }
            QPushButton:hover { color: #2980B9; }
        """)
        self.agree_link_btn.clicked.connect(self._on_details_link)
        agree_row.addWidget(self.agree_link_btn)
        agree_row.addStretch()
        body.addLayout(agree_row)

        body.addSpacing(18)

        self.btn_enter = QPushButton()
        self.btn_enter.setStyleSheet("""
            QPushButton { background-color: #27AE60; color: white; border-radius: 6px; font-weight: bold; font-size: 13px; padding: 10px 20px; }
            QPushButton:hover { background-color: #229954; }
            QPushButton:disabled { background-color: #BDC3C7; color: #7F8C8D; }
        """)
        self.btn_enter.setEnabled(False)
        self.btn_enter.setMinimumHeight(42)
        self.btn_enter.setCursor(Qt.PointingHandCursor)
        self.btn_enter.clicked.connect(self._on_enter)
        body.addWidget(self.btn_enter)

        outer.addLayout(body)

        self._refresh_texts()

    def _select_lang(self, lang):
        self._lang = lang
        self._refresh_texts()

    def _refresh_texts(self):
        set_language(self._lang)
        self.tagline_lbl.setText(t("app.subtitle"))
        self.lang_lbl.setText(t("gate.choose_language"))
        active_style = ("QPushButton { background-color: #1B5E8C; color: white; "
                         "border: 1px solid #1B5E8C; border-radius: 6px; font-weight: bold; }")
        inactive_style = ("QPushButton { background-color: #F0F3F5; color: #2C3E50; "
                           "border: 1px solid #D5DBE1; border-radius: 6px; } "
                           "QPushButton:hover { background-color: #E8ECF1; }")
        self.btn_lang_zh.setStyleSheet(active_style if self._lang == "zh_CN" else inactive_style)
        self.btn_lang_en.setStyleSheet(active_style if self._lang == "en_US" else inactive_style)
        self.agree_lbl.setText(t("gate.agree_prefix"))
        self.agree_link_btn.setText(t("gate.agree_link"))
        self.btn_enter.setText(t("gate.enter"))

    def _on_details_link(self):
        dlg = GateDetailsDialog(self)
        dlg.exec()

    def _on_check_changed(self, _state):
        self.btn_enter.setEnabled(self.agree_check.isChecked())

    def _on_enter(self):
        save_settings(license_agreed=True, license_agreed_version=APP_VERSION, ui_language=self._lang)
        self.accept()

    def _on_exit(self):
        self.reject()


class NewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("dlg.new_project"))
        self.setMinimumWidth(450)
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(t("dlg.name_placeholder"))
        form.addRow(t("dlg.name"), self.name_input)

        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(80)
        self.desc_input.setPlaceholderText(t("dlg.desc_placeholder"))
        form.addRow(t("dlg.desc"), self.desc_input)

        self.industry_input = QComboBox()
        for value, key in zip(INDUSTRIES, INDUSTRY_KEYS):
            self.industry_input.addItem(t(key), value)
        form.addRow(t("dlg.industry"), self.industry_input)

        self.scale_input = QComboBox()
        self.scale_input.addItems([t("dlg.scale_5"), t("dlg.scale_10")])
        form.addRow(t("dlg.scale"), self.scale_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return {
            'name': self.name_input.text() or t("dlg.unnamed_project"),
            'description': self.desc_input.toPlainText(),
            'industry': self.industry_input.currentData(),
            'importance_scale': 5 if self.scale_input.currentIndex() == 0 else 10,
        }


class ProjectPickerDialog(QDialog):
    """Pick an existing project — used by File > 打开项目 / 删除项目."""

    def __init__(self, db, mode='open', parent=None):
        super().__init__(parent)
        self.selected_id = None
        self.setWindowTitle(t("proj.open_title") if mode == 'open' else t("proj.delete_title"))
        self.setMinimumSize(560, 420)
        layout = QVBoxLayout(self)

        projects = db.list_projects()

        self.list = QListWidget()
        self.list.setStyleSheet("""
            QListWidget {
                border: 1px solid #D5DBE1;
                border-radius: 8px;
                background: white;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 14px;
                border-bottom: 1px solid #EEF0F2;
            }
            QListWidget::item:hover {
                background-color: #EBF5FB;
            }
            QListWidget::item:selected {
                background-color: #D4E6F1;
                color: #1B5E8C;
            }
        """)
        for p in projects:
            industry = p['industry']
            if industry in INDUSTRIES:
                industry = t(INDUSTRY_KEYS[INDUSTRIES.index(industry)])
            item = QListWidgetItem(t("proj.row_line", name=p['name'], industry=industry, updated_at=p['updated_at']))
            item.setData(Qt.UserRole, p['id'])
            self.list.addItem(item)
        self.list.itemDoubleClicked.connect(self._accept_current)
        layout.addWidget(self.list)

        if not projects:
            hint = QLabel(t("proj.no_projects_hint"))
            hint.setStyleSheet("color: #7F8C8D; padding: 4px;")
            layout.addWidget(hint)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ok_btn = buttons.button(QDialogButtonBox.Ok)
        ok_btn.setText(t("proj.open_btn") if mode == 'open' else t("proj.delete_btn"))
        if mode == 'delete':
            ok_btn.setObjectName("danger")
        buttons.accepted.connect(self._accept_current)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _accept_current(self):
        item = self.list.currentItem()
        if not item:
            QMessageBox.information(self, t("common.hint"), t("proj.select_first"))
            return
        self.selected_id = item.data(Qt.UserRole)
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # ── Load license ──
        self.license_info = load_license()
        self.edition = self.license_info.get("edition", EDITION_FREE)
        self.setMinimumSize(900, 600)
        screen = QGuiApplication.primaryScreen().geometry()
        w, h = min(1360, screen.width() - 80), min(880, screen.height() - 80)
        self.resize(w, h)
        self.move((screen.width() - w) // 2, (screen.height() - h) // 2)

        # ── Set icon ──
        icon_path = os.path.join(_APP_DIR, "assets", "qfd.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            png_path = os.path.join(_APP_DIR, "assets", "icon_256.png")
            if os.path.exists(png_path):
                self.setWindowIcon(QIcon(png_path))

        self.db = Database()
        self.db.connect("qfd_data.db")

        self.project_id = None
        self.current_phase = 1

        self._setup_menu()
        self._setup_ui()
        self._connect_signals()
        self._update_window_title()
        self._restore_last_project()

        # Auto-save timer
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self._auto_save)
        self.auto_save_timer.start(60000)  # 60 seconds

        # Status bar
        self.statusBar().showMessage(t("app.ready"))

        # Check for a newer version shortly after startup (non-blocking UI-wise,
        # delayed so it never slows down the initial window paint)
        QTimer.singleShot(1500, self._check_for_update)

    def _check_for_update(self):
        try:
            info = check_for_update()
        except Exception:
            info = None
        if not info or not info.get("available"):
            return
        notes = t("update.notes_prefix", body=info['notes']) if info.get("notes") else ""
        reply = QMessageBox.question(self, t("update.available_title"),
            t("update.available_body", version=info['version'], current=APP_VERSION, notes=notes),
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            url = info.get("download_url")
            if url:
                import webbrowser
                webbrowser.open(url)
            else:
                QMessageBox.information(self, t("common.hint"), t("update.no_link"))

    def _setup_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu(t("menu.file"))
        file_menu.addAction(t("menu.new_project"), self._create_project)
        file_menu.addAction(t("menu.open_project"), self._menu_open_project)
        self.switch_project_menu = file_menu.addMenu(t("menu.switch_project"))
        self.switch_project_menu.aboutToShow.connect(self._populate_switch_project_menu)
        file_menu.addAction(t("menu.new_demo"), self._load_demo)
        file_menu.addAction(t("menu.import_project"), self._import_project)
        file_menu.addSeparator()
        file_menu.addAction(t("menu.delete_project"), self._menu_delete_project)
        file_menu.addSeparator()
        file_menu.addAction(t("menu.back_home"), self._go_home)
        file_menu.addSeparator()
        file_menu.addAction(t("menu.exit"), self.close)

        license_menu = menubar.addMenu(t("menu.license"))
        license_menu.addAction(t("menu.license_manage"), self._show_license_dialog)
        license_menu.addAction(t("menu.view_license"), self._show_license_text)

        help_menu = menubar.addMenu(t("menu.help"))
        help_menu.addAction(t("menu.help_manual"), self._show_help)
        help_menu.addSeparator()
        help_menu.addAction(t("menu.about"), self._show_about)

    def _edition_tag(self):
        if self.edition == EDITION_COMMERCIAL:
            return t("app.commercial")
        if self.edition == EDITION_LICENSED:
            return t("app.licensed")
        return t("app.free")

    def _show_about(self):
        QMessageBox.information(self, t("menu.about"),
            t("about.body", version=APP_VERSION, edition=self._edition_tag()))

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet(f"background-color: {COLORS['primary_dark']};")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo
        # ── Compact single-row header: language toggle (in the logo's old spot) + title + badge ──
        logo_frame = QFrame()
        logo_frame.setStyleSheet(f"background-color: {COLORS['primary_dark']}; padding: 6px 6px;")
        logo_layout = QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(4, 4, 4, 4)
        logo_layout.setSpacing(6)

        title_lbl = QLabel("OpenQFD")
        title_lbl.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        title_lbl.setStyleSheet("color: white;")
        title_lbl.setMinimumWidth(title_lbl.fontMetrics().horizontalAdvance("OpenQFD") + 8)

        # Segmented zh/EN toggle. Deliberately sized by its own content (small font +
        # small padding) rather than force-fit to a pixel height: QPushButton's sizeHint
        # vs. an externally forced setFixedHeight fight each other in Qt's layout pass
        # and can produce an off-center / overflowing result, especially under
        # fractional DPI scaling. Letting the layout size itself naturally avoids that.
        lang_frame = QFrame()
        lang_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255,255,255,0.15);
                border: 1px solid rgba(255,255,255,0.4);
                border-radius: 3px;
                padding: 0px;
                margin: 0px;
            }
        """)
        lang_frame_layout = QHBoxLayout(lang_frame)
        lang_frame_layout.setContentsMargins(1, 1, 1, 1)
        lang_frame_layout.setSpacing(1)
        self.btn_lang_zh_side = QPushButton("中")
        self.btn_lang_en_side = QPushButton("EN")
        for b in (self.btn_lang_zh_side, self.btn_lang_en_side):
            b.setCursor(Qt.PointingHandCursor)
            b.setFlat(True)
        self.btn_lang_zh_side.clicked.connect(lambda: self._select_language("zh_CN"))
        self.btn_lang_en_side.clicked.connect(lambda: self._select_language("en_US"))
        self._update_lang_btn()
        for b in (self.btn_lang_zh_side, self.btn_lang_en_side):
            b.setFixedHeight(b.sizeHint().height())
        # Derive the frame's height from the button's own (now-fixed) height so the two
        # can never disagree — an independently-guessed frame height is what caused the
        # earlier overflow/off-center bug.
        margins = lang_frame_layout.contentsMargins()
        lang_frame.setFixedHeight(
            self.btn_lang_zh_side.height() + margins.top() + margins.bottom() + 2)  # +2 for the 1px border on each side
        lang_frame_layout.addWidget(self.btn_lang_zh_side)
        lang_frame_layout.addWidget(self.btn_lang_en_side)
        lang_frame_layout.invalidate()
        lang_frame_layout.activate()
        logo_layout.addWidget(lang_frame)

        logo_layout.addWidget(title_lbl)
        logo_layout.addStretch()

        badge_text = t("badge.free") if self.edition == EDITION_FREE else t("badge.licensed")
        badge_color = "#F39C12" if self.edition == EDITION_FREE else "#2ECC71"
        badge = QLabel(badge_text)
        badge.setStyleSheet(f"color: {badge_color}; font-size: 9px; font-weight: bold;")
        logo_layout.addWidget(badge)

        sidebar_layout.addWidget(logo_frame)

        # Phase selector
        self.phase_selector = QComboBox()
        self.phase_selector.setStyleSheet("QComboBox { color: white; background-color: #1B5E8C; }")
        for p in PHASE_NAMES:
            self.phase_selector.addItem(t(f"phase.{p}"), p)
        self.phase_selector.currentIndexChanged.connect(self._update_phase_checkmarks)
        self.phase_selector.currentIndexChanged.connect(self._on_phase_changed)
        self._update_phase_checkmarks()
        sidebar_layout.addWidget(self.phase_selector)

        # Nav list
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet(SIDEBAR_STYLE)
        self.nav_items = [
            ("🏠", t("nav.overview"),     "project"),
            ("📋", t("nav.voc"),          "voc"),
            ("🔧", t("nav.ctq"),          "ctq"),
            ("🏢", t("nav.competition"),   "competition"),
            ("📊", t("nav.hoq"),          "hoq"),
            ("📈", t("nav.kano"),          "kano"),
            ("⚖️", t("nav.ahp"),           "ahp"),
            ("📉", t("nav.pareto"),        "pareto"),
            ("🔄", t("nav.phase"),         "phase"),
            ("💡", t("nav.triz"),          "triz"),
            ("⚠️", t("nav.fmea"),          "fmea"),
            ("🧪", t("nav.doe"),           "doe"),
            ("🔗", t("nav.dsm"),           "dsm"),
            ("📤", t("nav.export"),        "export_full"),
            ("📌", t("nav.version"),       "version"),
            ("⬅️", t("nav.back"),          None),
        ]
        for icon, text, module in self.nav_items:
            locked = (module and not is_module_allowed(module, self.edition))
            suffix = "  🔒" if locked else ""
            item = QListWidgetItem(f"  {icon}  {text}{suffix}")
            item.setSizeHint(QSize(200, 36))
            if locked:
                item.setForeground(QColor("#7F8C8D"))
            self.nav_list.addItem(item)
        self.nav_list.currentRowChanged.connect(self._on_nav_changed)
        sidebar_layout.addWidget(self.nav_list)

        main_layout.addWidget(self.sidebar)

        # Content stack
        self.stack = QStackedWidget()

        # Page 0: Welcome / poster (shown before any project is open)
        self.welcome_view = WelcomeView()
        self.stack.addWidget(self.welcome_view)

        # Page 1-15: Module views
        self.overview_widget = QWidget()       # 1
        self.voc_view = VOCManagerView(self.db) # 2
        self.ctq_view = CTQManagerView(self.db) # 3
        self.comp_view = CompetitionView(self.db) # 4 — before HOQ
        self.hoq_view = HOQMatrixView(self.db)  # 5
        self.kano_view = KanoView(self.db)      # 6
        self.ahp_view = AHPView(self.db)        # 7
        self.pareto_view = ParetoView(self.db)  # 8
        self.phase_view = PhaseView(self.db)    # 9
        self.triz_view = TRIZView(self.db)      # 10
        self.fmea_view = FMEAView(self.db)      # 11
        self.doe_view = DOEView(self.db)        # 12
        self.dsm_view = DSMView(self.db)        # 13
        self.export_view = ExportView(self.db)  # 14
        self.version_view = VersionView(self.db) # 15

        for w in [self.overview_widget, self.voc_view, self.ctq_view,
                  self.comp_view, self.hoq_view, self.kano_view,
                  self.ahp_view, self.pareto_view, self.phase_view,
                  self.triz_view, self.fmea_view, self.doe_view, self.dsm_view,
                  self.export_view, self.version_view]:
            self.stack.addWidget(w)

        self._setup_overview()
        main_layout.addWidget(self.stack)

    def _setup_overview(self):
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
        from matplotlib.figure import Figure
        from utils.fonts import setup_matplotlib_fonts
        setup_matplotlib_fonts()

        outer_layout = QVBoxLayout(self.overview_widget)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        outer_layout.addWidget(scroll)

        # Center the content and cap its width — on a very wide window, letting
        # the KPI cards/charts/quick-actions stretch to the full width distorts
        # the matplotlib figure (pie chart becomes oval, bars spread out) and
        # leaves the cards looking sparse.
        center_wrapper = QWidget()
        center_layout = QHBoxLayout(center_wrapper)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.addStretch()

        content = QWidget()
        content.setMaximumWidth(1300)
        center_layout.addWidget(content)
        center_layout.addStretch()
        scroll.setWidget(center_wrapper)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Header: title + one-line quick facts
        self.overview_title = QLabel(t("nav.overview"))
        self.overview_title.setObjectName("title")
        self.overview_title.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        layout.addWidget(self.overview_title)

        self.overview_info = QLabel("")
        self.overview_info.setWordWrap(True)
        self.overview_info.setStyleSheet("font-size: 13px; color: #7F8C8D;")
        layout.addWidget(self.overview_info)

        # Basic-data stat cards (icon badge + number + label)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)
        self.stat_cards = {}
        stat_configs = [
            ("voc", "📋", t("overview.voc_count"), "#5DADE2"),
            ("ctq", "🔧", t("overview.ctq_count"), "#F5B041"),
            ("rel", "📊", t("overview.rel_count"), "#58D68D"),
            ("comp", "🏢", t("overview.comp_count"), "#BB8FCE"),
        ]
        for key, icon, label, color in stat_configs:
            card = QFrame()
            card.setStyleSheet("QFrame { background: white; border-radius: 14px; }")
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(16, 14, 16, 14)
            badge = QLabel(icon)
            badge.setFixedSize(44, 44)
            badge.setAlignment(Qt.AlignCenter)
            badge.setStyleSheet(f"background-color: {color}; border-radius: 22px; font-size: 18px;")
            card_layout.addWidget(badge)
            text_col = QVBoxLayout()
            text_col.setSpacing(0)
            count_lbl = QLabel("0")
            count_lbl.setFont(QFont("Microsoft YaHei", 22, QFont.Bold))
            count_lbl.setStyleSheet(f"color: {COLORS['text']};")
            text_col.addWidget(count_lbl)
            name_lbl = QLabel(label)
            name_lbl.setStyleSheet("color: #7F8C8D; font-size: 12px;")
            text_col.addWidget(name_lbl)
            card_layout.addLayout(text_col)
            card_layout.addStretch()
            stats_layout.addWidget(card)
            self.stat_cards[key] = count_lbl
        layout.addLayout(stats_layout)

        # Core decision KPIs: M (market/customer competitiveness) and T (technical
        # competitiveness), for "our own product" — the headline numbers HOQ exists
        # to produce.
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(12)
        self.kpi_cards = {}
        kpi_configs = [
            ("m", t("overview.market_index"), t("overview.market_index_desc")),
            ("t", t("overview.tech_index"), t("overview.tech_index_desc")),
        ]
        for key, title, hint in kpi_configs:
            card = QFrame()
            card.setMinimumHeight(90)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(18, 12, 18, 12)
            title_lbl = QLabel(title)
            title_lbl.setStyleSheet(f"color: {COLORS['text']}; font-size: 13px; font-weight: bold;")
            card_layout.addWidget(title_lbl)
            row = QHBoxLayout()
            val_lbl = QLabel("--")
            val_lbl.setFont(QFont("Microsoft YaHei", 30, QFont.Bold))
            row.addWidget(val_lbl)
            row.addStretch()
            card_layout.addLayout(row)
            hint_lbl = QLabel(hint)
            hint_lbl.setWordWrap(True)
            hint_lbl.setStyleSheet("color: #7F8C8D; font-size: 11px;")
            card_layout.addWidget(hint_lbl)
            kpi_layout.addWidget(card)
            self.kpi_cards[key] = {'card': card, 'value': val_lbl, 'hint': hint_lbl, 'default_hint': hint}
        layout.addLayout(kpi_layout)

        # Charts: Kano distribution + HOQ's actual outputs — Top-5 VOC priority
        # (right-wall Wi) and Top-5 CTQ priority (floor Tai)
        charts_group = QGroupBox(t("overview.hoq_output"))
        charts_layout = QVBoxLayout(charts_group)
        self.overview_fig = Figure(figsize=(12, 3.3), dpi=100)
        self.overview_canvas = FigureCanvasQTAgg(self.overview_fig)
        charts_layout.addWidget(self.overview_canvas)
        layout.addWidget(charts_group, 1)

        # Readiness checklist
        readiness_group = QGroupBox(t("overview.readiness"))
        readiness_layout = QVBoxLayout(readiness_group)
        self.readiness_label = QLabel("")
        self.readiness_label.setWordWrap(True)
        self.readiness_label.setStyleSheet("font-size: 13px; line-height: 1.9;")
        readiness_layout.addWidget(self.readiness_label)
        layout.addWidget(readiness_group)

    def _connect_signals(self):
        # Data change signals
        self.voc_view.data_changed.connect(self._on_data_changed)
        self.ctq_view.data_changed.connect(self._on_ctq_data_changed)
        self.hoq_view.data_changed.connect(self._on_data_changed)
        self.comp_view.data_changed.connect(self._on_data_changed)
        self.kano_view.data_changed.connect(self._on_data_changed)
        self.ahp_view.weights_computed.connect(lambda _: self._refresh_all())

        # Phase view
        self.phase_view.phase_changed.connect(self._switch_to_phase)

        # Version view
        self.version_view.version_restored.connect(self._refresh_all)

    def _update_window_title(self):
        title = f"{t('app.title')} V{APP_VERSION} — {self._edition_tag()}"
        if self.project_id:
            project = self.db.get_project(self.project_id)
            if project:
                title += f" — {project['name']}"
        self.setWindowTitle(title)

    def _restore_last_project(self):
        """Auto-load the project that was open when the app last closed.
        On true first-ever use (no saved project and no projects in the DB
        at all), auto-create and load the sample project instead of showing
        a blank welcome page."""
        last_id = load_settings().get('last_project_id')
        if last_id and self.db.get_project(last_id):
            self._open_project_by_id(last_id)
            return
        if not self.db.list_projects():
            self._load_demo(silent=True)
        else:
            self._show_welcome()

    def _show_welcome(self):
        """Full reset to the no-project state (used when there truly is no
        project to show, e.g. after deleting the currently open project)."""
        self.project_id = None
        self._go_home()
        self._update_window_title()

    def _go_home(self):
        """Return to the welcome/home page without unloading the current
        project, so navigating back into a module still shows its data."""
        self.stack.setCurrentIndex(0)
        self.nav_list.blockSignals(True)
        self.nav_list.setCurrentRow(-1)
        self.nav_list.blockSignals(False)
        self._update_welcome_poster()
        self.statusBar().showMessage(t("app.ready"))

    def _update_welcome_poster(self):
        """Feed the welcome poster's HOQ mockup real data from the current
        project (top 4 VOCs/CTQs by importance) instead of the built-in
        placeholder sample, falling back to the placeholder if there's no
        project loaded or it has no VOC/CTQ data yet."""
        if not self.project_id:
            self.welcome_view.canvas.set_real_data([], [], {}, {}, [])
            return

        all_vocs = [dict(v) for v in self.db.get_vocs(self.project_id, self.current_phase)]
        all_ctqs = [dict(c) for c in self.db.get_ctqs(self.project_id, self.current_phase)]
        if not all_vocs or not all_ctqs:
            self.welcome_view.canvas.set_real_data([], [], {}, {}, [])
            return

        vocs = sorted(all_vocs, key=lambda v: v.get('importance') or 0, reverse=True)[:4]
        ctqs = all_ctqs[:4]
        voc_idx = {v['id']: i for i, v in enumerate(vocs)}
        ctq_idx = {c['id']: i for i, c in enumerate(ctqs)}

        rels_raw = [dict(r) for r in self.db.get_relationships(self.project_id, self.current_phase)]
        rel = {}
        for r in rels_raw:
            i, j = voc_idx.get(r['voc_id']), ctq_idx.get(r['ctq_id'])
            if i is not None and j is not None and r.get('strength'):
                rel[(i, j)] = r['strength']

        roof_raw = self.db.get_roof_correlations(self.project_id, self.current_phase)
        roof = {}
        for cr in roof_raw:
            i, j = ctq_idx.get(cr['ctq_id_1']), ctq_idx.get(cr['ctq_id_2'])
            if i is not None and j is not None:
                if i > j:
                    i, j = j, i
                roof[(i, j)] = cr['correlation']

        importance = HOQEngine.compute_importance(all_vocs, all_ctqs, rels_raw)
        tai_vals = [importance.get(c['id'], {}).get('relative_importance', 0) for c in ctqs]
        max_tai = max(tai_vals) if tai_vals and max(tai_vals) > 0 else 1
        tai_norm = [v / max_tai for v in tai_vals]

        self.welcome_view.canvas.set_real_data(
            [v['name'] for v in vocs], [c['name'] for c in ctqs], rel, roof, tai_norm)

    def _create_project(self):
        dlg = NewProjectDialog(self)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            pid = self.db.create_project(**data)
            self._open_project_by_id(pid)

    def _menu_open_project(self):
        dlg = ProjectPickerDialog(self.db, mode='open', parent=self)
        if dlg.exec() == QDialog.Accepted and dlg.selected_id:
            self._open_project_by_id(dlg.selected_id)

    def _populate_switch_project_menu(self):
        """Rebuilt each time the submenu opens so it always reflects the
        most-recently-updated projects."""
        self.switch_project_menu.clear()
        projects = self.db.list_projects()[:8]
        if not projects:
            act = self.switch_project_menu.addAction(t("proj.none_placeholder"))
            act.setEnabled(False)
            return
        for p in projects:
            label = f"✓ {p['name']}" if p['id'] == self.project_id else p['name']
            act = self.switch_project_menu.addAction(label)
            act.triggered.connect(lambda checked=False, pid=p['id']: self._open_project_by_id(pid))

    def _open_project_by_id(self, pid):
        self.project_id = pid
        self.current_phase = 1
        self.phase_selector.setCurrentIndex(0)

        # Set project on all views
        self.voc_view.set_project(pid, self.current_phase)
        self.ctq_view.set_project(pid, self.current_phase)
        self.hoq_view.set_project(pid, self.current_phase)
        self.comp_view.set_project(pid, self.current_phase)
        self.kano_view.set_project(pid, self.current_phase)
        self.ahp_view.set_project(pid, self.current_phase)
        self.pareto_view.set_project(pid, self.current_phase)
        self.phase_view.set_project(pid)
        self.fmea_view.set_project(pid, self.current_phase)
        self.dsm_view.set_project(pid, self.current_phase)
        self.export_view.set_project(pid, self.current_phase)
        self.version_view.set_project(pid)

        self._update_overview()
        self.nav_list.setCurrentRow(0)
        self.stack.setCurrentIndex(1)

        project = self.db.get_project(pid)
        self.statusBar().showMessage(t("msg.project_opened", name=project['name']))
        self._update_window_title()
        self._update_welcome_poster()
        save_settings(last_project_id=pid)

    def _menu_delete_project(self):
        dlg = ProjectPickerDialog(self.db, mode='delete', parent=self)
        if dlg.exec() != QDialog.Accepted or not dlg.selected_id:
            return
        pid = dlg.selected_id
        project = self.db.get_project(pid)
        reply = QMessageBox.question(self, t("msg.confirm_delete_title"),
            t("msg.confirm_delete_project", name=project['name'] if project else pid),
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete_project(pid)
            if self.project_id == pid:
                self._show_welcome()

    def _import_project(self):
        path, _ = QFileDialog.getOpenFileName(self, t("msg.import_project_title"), "",
                                              t("msg.import_json_filter"))
        if not path:
            return
        try:
            import json
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            project_data = data.get('project', {})
            pid = self.db.create_project(
                project_data.get('name', t("msg.import_project_title")),
                project_data.get('description', ''),
                project_data.get('industry', ''))

            # Import VOCs
            for v in data.get('vocs', []):
                self.db.add_voc(pid, v['name'], phase=v.get('phase', 1),
                              importance=v.get('importance', 3),
                              description=v.get('description', ''),
                              source=v.get('source', ''),
                              kano_type=v.get('kano_type', ''))
            # Import CTQs
            for c in data.get('ctqs', []):
                self.db.add_ctq(pid, c['name'], phase=c.get('phase', 1),
                              unit=c.get('unit', ''),
                              direction=c.get('direction', 'higher_better'),
                              target_value=c.get('target_value', ''),
                              difficulty=c.get('difficulty', 3))

            self._open_project_by_id(pid)
            QMessageBox.information(self, t("common.success"), t("msg.import_complete"))
        except Exception as e:
            QMessageBox.critical(self, t("msg.import_failed"), str(e))

    def _load_demo(self, silent=False):
        """Create a new sample project with demo data. Repeated invocations
        get a numbered suffix (示例: 智能手表产品QFD 2, 3, ...) so multiple
        sample projects can coexist and stay distinguishable."""
        base_name = "示例: 智能手表产品QFD"
        existing_names = {p['name'] for p in self.db.list_projects()}
        name = base_name
        n = 2
        while name in existing_names:
            name = f"{base_name} {n}"
            n += 1

        pid = self.db.create_project(
            name,
            "智能手表产品开发QFD分析示例项目",
            "消费电子")

        # Demo VOCs (name, importance, kano, source, improvement_ratio, sales_point, planned_level)
        vocs_data = [
            ("电池续航长", 5.0, "M", "市场调研", 1.5, 1.5, 5.0),
            ("屏幕显示清晰", 4.0, "O", "客户访谈", 1.2, 1.2, 4.0),
            ("佩戴舒适", 4.5, "M", "投诉反馈", 1.0, 1.0, 4.0),
            ("防水性能好", 3.5, "M", "行业标准", 1.3, 1.2, 4.0),
            ("健康监测准确", 4.0, "O", "市场调研", 1.4, 1.5, 4.5),
            ("外观时尚", 3.0, "A", "客户访谈", 1.0, 1.0, 3.5),
            ("操作简便", 3.5, "O", "客户访谈", 1.2, 1.0, 4.0),
            ("充电速度快", 2.5, "A", "竞品分析", 1.0, 1.0, 3.0),
        ]
        voc_ids = []
        for name, imp, kano, source, ir, sp, pl in vocs_data:
            vid = self.db.add_voc(pid, name, importance=imp, kano_type=kano,
                                 source=source, improvement_ratio=ir, sales_point=sp,
                                 planned_level=pl)
            voc_ids.append(vid)

        # Demo CTQs
        ctqs_data = [
            ("电池容量", "mAh", "higher_better", "500", "350", 3.0),
            ("屏幕分辨率", "PPI", "higher_better", "400", "326", 2.0),
            ("整机重量", "g", "lower_better", "35", "45", 2.5),
            ("防水等级", "ATM", "higher_better", "5", "3", 3.5),
            ("心率精度", "%", "lower_better", "±2", "±5", 4.0),
            ("外壳材料强度", "HV", "higher_better", "300", "250", 2.0),
            ("触控响应时间", "ms", "lower_better", "50", "80", 2.5),
            ("充电功率", "W", "higher_better", "10", "5", 3.0),
        ]
        ctq_ids = []
        for name, unit, direction, target, current, diff in ctqs_data:
            cid = self.db.add_ctq(pid, name, unit=unit, direction=direction,
                                 target_value=target, current_value=current, difficulty=diff)
            ctq_ids.append(cid)

        # Demo relationships (sparse)
        rels = [
            (0, 0, 9), (0, 7, 3),  # battery life -> battery capacity, charge power
            (1, 1, 9), (1, 6, 3),  # clear display -> resolution, response time
            (2, 2, 9), (2, 5, 3),  # comfort -> weight, material
            (3, 3, 9),             # waterproof -> waterproof rating
            (4, 4, 9), (4, 0, 1),  # health monitoring -> heart rate accuracy
            (5, 5, 3), (5, 2, 3),  # stylish -> material, weight
            (6, 6, 9), (6, 1, 1),  # easy to use -> response time
            (7, 7, 9), (7, 0, 3),  # fast charge -> charge power, battery capacity
        ]
        for vi, ci, strength in rels:
            if vi < len(voc_ids) and ci < len(ctq_ids):
                self.db.set_relationship(pid, voc_ids[vi], ctq_ids[ci], strength)

        # Demo roof correlations
        roofs = [
            (0, 2, '--'),  # battery vs weight: strong negative
            (0, 7, '+'),   # battery vs charge power: positive
            (1, 6, '+'),   # resolution vs response time: positive
            (2, 5, '-'),   # weight vs material strength: negative
        ]
        for ci1, ci2, corr in roofs:
            if ci1 < len(ctq_ids) and ci2 < len(ctq_ids):
                self.db.set_roof_correlation(pid, ctq_ids[ci1], ctq_ids[ci2], corr)

        # Demo competitors
        self_id = self.db.add_competitor(pid, "我方产品", is_self=True, color='#3498DB')
        comp1_id = self.db.add_competitor(pid, "Apple Watch", color='#E74C3C')
        comp2_id = self.db.add_competitor(pid, "Galaxy Watch", color='#2ECC71')

        # Demo competitor scores
        self_scores = [3.5, 3.0, 4.0, 3.0, 3.0, 3.5, 3.5, 2.5]
        apple_scores = [4.0, 4.5, 3.5, 4.0, 4.0, 4.5, 4.0, 4.0]
        galaxy_scores = [4.5, 4.0, 3.0, 4.0, 3.5, 3.5, 3.5, 3.5]

        for i, vid in enumerate(voc_ids):
            # Self competitor's score goes through the sync helper so voc.current_level
            # (Ui) — used by Ri/Wai and the dashboard's VOC priority ranking — gets set too.
            self.db.sync_self_voc_score(pid, vid, self_scores[i])
            self.db.set_competitor_voc_score(comp1_id, vid, apple_scores[i])
            self.db.set_competitor_voc_score(comp2_id, vid, galaxy_scores[i])

        # Demo CTQ competitor benchmark values
        # CTQs: 电池容量, 屏幕分辨率, 整机重量, 防水等级, 心率精度, 外壳强度, 触控响应, 充电功率
        self_ctq  = ["350", "326", "45", "3", "±5", "250", "80", "5"]
        apple_ctq = ["430", "400", "38", "5", "±2", "300", "50", "7.5"]
        galaxy_ctq= ["470", "390", "42", "5", "±3", "280", "60", "10"]
        for i, cid in enumerate(ctq_ids):
            # Self competitor goes through the sync helper (keeps ctq.current_value
            # identical instead of relying on it happening to match).
            self.db.sync_self_ctq_score(pid, cid, self_ctq[i])
            self.db.set_competitor_ctq_score(comp1_id, cid, apple_ctq[i])
            self.db.set_competitor_ctq_score(comp2_id, cid, galaxy_ctq[i])

        self._open_project_by_id(pid)
        if not silent:
            QMessageBox.information(self, t("msg.demo_title"), t("msg.demo_created", name=name))

    def _on_nav_changed(self, row):
        if row < 0:
            return
        if row == len(self.nav_items) - 1:  # Return to welcome page
            self._go_home()
            return

        if not self.project_id:
            QMessageBox.information(self, t("common.hint"), t("msg.no_project_first"))
            return

        # License gating — locked modules jump straight to license activation
        module = NAV_MODULE_MAP.get(row)
        if module and not is_module_allowed(module, self.edition):
            self.statusBar().showMessage(
                t("lic.locked_status", name=self.nav_items[row][1]), 4000)
            self._show_license_dialog()
            return

        self.stack.setCurrentIndex(row + 1)

        # Refresh views when navigating to them
        if row == 0:
            self._update_overview()
        elif row == 1:  # VOC
            self.voc_view.refresh()
        elif row == 2:  # CTQ
            self.ctq_view.refresh()
        elif row == 3:  # Competition (CBA)
            self.comp_view.refresh()
        elif row == 4:  # HOQ
            self.hoq_view.refresh()
        elif row == 5:  # Kano
            self.kano_view.refresh()
        elif row == 6:  # AHP
            self.ahp_view.refresh()
        elif row == 7:  # Pareto
            self.pareto_view._generate_chart()
        elif row == 8:  # Phase
            self.phase_view.refresh()
        elif row == 9:  # TRIZ (no project data needed)
            pass
        elif row == 10:  # FMEA
            pass
        elif row == 11:  # DOE
            pass
        elif row == 12:  # DSM
            pass

    def _show_license_dialog(self):
        dlg = LicenseDialog(self.license_info, self)
        dlg.exec()

    def _show_license_text(self):
        dlg = LicenseTextDialog(self)
        dlg.exec()

    def _show_help(self):
        dlg = HelpDialog(self)
        dlg.exec()

    def _update_lang_btn(self):
        is_zh = get_language() == "zh_CN"
        active_style = """
            QPushButton {
                background-color: white; color: #1B5E8C; border: none;
                border-radius: 2px; padding: 1px 4px; font-size: 8px; font-weight: bold;
            }
        """
        inactive_style = """
            QPushButton {
                background-color: transparent; color: rgba(255,255,255,0.6); border: none;
                border-radius: 2px; padding: 1px 4px; font-size: 8px; font-weight: bold;
            }
            QPushButton:hover { color: white; }
        """
        self.btn_lang_zh_side.setStyleSheet(active_style if is_zh else inactive_style)
        self.btn_lang_en_side.setStyleSheet(inactive_style if is_zh else active_style)

    def _select_language(self, lang):
        if lang == get_language():
            return
        set_language(lang)
        self._update_lang_btn()
        reply = QMessageBox.question(self, t("lang.confirm_title"), t("lang.confirm_body"),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self._reload_ui()

    def _reload_ui(self):
        """Rebuild the whole window in-place instead of restarting the OS process.
        PyInstaller onefile builds extract to one deterministic temp folder per exe
        build; launching a second instance (QProcess.startDetached) while the first
        is still exiting races on that shared folder and can crash with spurious
        "module partially initialized" / missing-file errors. An in-process rebuild
        sidesteps that entirely and is also faster."""
        project_id = self.project_id
        if project_id:
            self.db.update_project(project_id)
        new_win = MainWindow()
        if project_id:
            new_win._open_project_by_id(project_id)
        new_win.show()
        QApplication.instance()._openqfd_main_window = new_win  # keep alive (no other ref)
        self.close()

    def _update_phase_checkmarks(self):
        """Prefix the currently-selected phase item with a checkmark in the popup."""
        current = self.phase_selector.currentIndex()
        self.phase_selector.blockSignals(True)
        for i in range(self.phase_selector.count()):
            p = self.phase_selector.itemData(i)
            name = t(f"phase.{p}") if p in PHASE_NAMES else ""
            prefix = "✓ " if i == current else "　"  # full-width space keeps items aligned
            self.phase_selector.setItemText(i, f"{prefix}{name}")
        self.phase_selector.blockSignals(False)

    def _on_phase_changed(self):
        phase = self.phase_selector.currentData()
        if not phase or not self.project_id:
            return
        self.current_phase = phase
        self.voc_view.set_project(self.project_id, phase)
        self.ctq_view.set_project(self.project_id, phase)
        self.hoq_view.set_project(self.project_id, phase)
        self.comp_view.set_project(self.project_id, phase)
        self.kano_view.set_project(self.project_id, phase)
        self.ahp_view.set_project(self.project_id, phase)
        self.pareto_view.set_project(self.project_id, phase)
        self.fmea_view.set_project(self.project_id, phase)
        self.dsm_view.set_project(self.project_id, phase)
        self.export_view.set_project(self.project_id, phase)
        self.statusBar().showMessage(t("phase.status", name=t(f"phase.{phase}")))

    def _switch_to_phase(self, phase):
        self.phase_selector.setCurrentIndex(phase - 1)
        self.nav_list.setCurrentRow(1)  # Go to VOC view

    def _on_data_changed(self):
        self._update_overview()
        self.db.update_project(self.project_id)

    def _on_ctq_data_changed(self):
        """CTQ list changes affect the HOQ columns/roof and CBA's CTQ benchmark
        columns too — refresh those eagerly instead of waiting for the user to
        navigate into them, so e.g. the roof always reflects the current CTQ count."""
        self._on_data_changed()
        if self.project_id:
            self.hoq_view.refresh()
            self.comp_view.refresh()

    def _refresh_all(self):
        if not self.project_id:
            return
        p = self.current_phase
        self.voc_view.set_project(self.project_id, p)
        self.ctq_view.set_project(self.project_id, p)
        self.hoq_view.set_project(self.project_id, p)
        self.comp_view.set_project(self.project_id, p)
        self.kano_view.set_project(self.project_id, p)
        self.ahp_view.set_project(self.project_id, p)
        self.fmea_view.set_project(self.project_id, p)
        self.dsm_view.set_project(self.project_id, p)
        self.phase_view.set_project(self.project_id)
        self._update_overview()

    def _update_overview(self):
        if not self.project_id:
            return
        project = self.db.get_project(self.project_id)
        if not project:
            return

        industry = project['industry']
        if industry in INDUSTRIES:
            industry = t(INDUSTRY_KEYS[INDUSTRIES.index(industry)])

        self.overview_title.setText(f"📊 {project['name']}")
        self.overview_info.setText(
            t("project.industry_line", v=industry) +
            t("project.scale_line", v=project['importance_scale']) +
            t("project.created_line", v=project['created_at']) +
            t("project.updated_line", v=project['updated_at']) +
            t("project.desc_line", v=project['description'] or t("project.no_desc"))
        )

        # Stats
        vocs = [dict(v) for v in self.db.get_vocs(self.project_id, self.current_phase)]
        ctqs = [dict(c) for c in self.db.get_ctqs(self.project_id, self.current_phase)]
        rels = [dict(r) for r in self.db.get_relationships(self.project_id, self.current_phase)]
        comps = list(self.db.get_competitors(self.project_id))

        self.stat_cards['voc'].setText(str(len(vocs)))
        self.stat_cards['ctq'].setText(str(len(ctqs)))
        self.stat_cards['rel'].setText(str(len(rels)))
        self.stat_cards['comp'].setText(str(len(comps)))

        self._update_kpi_cards(vocs, ctqs, rels, comps)
        self._draw_overview_charts(vocs, ctqs, rels)
        self._update_readiness(vocs, ctqs, rels, comps)

    def _voc_priority_ranking(self, vocs):
        """Rank VOCs by the HOQ right-wall's normalized weight Wi = Wai/Sum(Wai),
        Wai = Ri*Si*Ii, Ri = Ti/Ui — mirrors hoq_view.py's right-wall columns."""
        rows = []
        for v in vocs:
            ui = v.get('current_level', 0) or 0
            ti = v.get('planned_level', 0) or 0
            ri = (ti / ui) if ui > 0 else 0
            si = v.get('sales_point', 1.0) or 1.0
            ii = v.get('importance', 0) or 0
            rows.append((v['name'], ri * si * ii))
        return sorted(rows, key=lambda x: x[1], reverse=True)

    def _compute_self_indices(self, vocs, ctqs, rels, comps):
        """M (market/customer satisfaction) and T (technical competitiveness) for
        the self-marked competitor. Mirrors hoq_view.py's floor (M) and basement
        (T) formulas — keep the two in sync if either changes."""
        self_comp = next((c for c in comps if c['is_self']), None)
        if not self_comp:
            return None, None

        scores = {s['voc_id']: s['score'] for s in self.db.get_competitor_voc_scores(self_comp['id'])}
        w_sum, t_ii = 0, 0
        for v in vocs:
            sc = scores.get(v['id'], 0)
            ii = v.get('importance', 0) or 0
            if sc and ii:
                w_sum += sc * ii
                t_ii += ii
        m = (w_sum / (t_ii * 5)) if t_ii > 0 else None

        t = None
        if ctqs and rels:
            importance = HOQEngine.compute_importance(vocs, ctqs, rels)
            comp_ctq_scores = {}
            for comp in comps:
                for s in self.db.get_competitor_ctq_scores(comp['id']):
                    comp_ctq_scores[(comp['id'], s['ctq_id'])] = s['value']
            t_sum, tai_sum = 0, 0
            for c in ctqs:
                tai = importance.get(c['id'], {}).get('absolute_importance', 0)
                try:
                    val = float(comp_ctq_scores.get((self_comp['id'], c['id']), ""))
                except (TypeError, ValueError):
                    val = 0
                all_vals = []
                for comp2 in comps:
                    try:
                        all_vals.append(float(comp_ctq_scores.get((comp2['id'], c['id']), "")))
                    except (TypeError, ValueError):
                        pass
                max_val = max(all_vals) if all_vals else 1
                min_val = min((v2 for v2 in all_vals if v2 > 0), default=1)
                direction = c.get('direction', 'higher_better')
                if max_val > 0 and val > 0:
                    norm = (min_val / val) if direction == 'lower_better' else (val / max_val)
                    t_sum += tai * norm
                    tai_sum += tai
            t = (t_sum / tai_sum) if tai_sum > 0 else None
        return m, t

    def _update_kpi_cards(self, vocs, ctqs, rels, comps):
        # (tier text color, light tint background)
        NO_DATA = ("#95A5A6", "#F4F6F6")
        HIGH = ("#27AE60", "#EAFAF1")
        MID = ("#E67E22", "#FEF5E7")
        LOW = ("#E74C3C", "#FDEDEC")

        m, tech = self._compute_self_indices(vocs, ctqs, rels, comps)
        for key, value in (('m', m), ('t', tech)):
            card = self.kpi_cards[key]
            if value is None:
                text_color, bg = NO_DATA
                card['value'].setText("--")
                card['hint'].setText(t("overview.no_self_hint") if not comps
                                      else card['default_hint'])
            else:
                text_color, bg = HIGH if value >= 0.8 else (MID if value >= 0.5 else LOW)
                card['value'].setText(f"{value*100:.0f}%")
                card['hint'].setText(card['default_hint'])
            card['card'].setStyleSheet(f"QFrame {{ background-color: {bg}; border-radius: 14px; }}")
            card['value'].setStyleSheet(f"color: {text_color};")

    def _draw_overview_charts(self, vocs, ctqs, rels):
        self.overview_fig.clear()
        if not vocs and not ctqs:
            ax = self.overview_fig.add_subplot(111)
            ax.text(0.5, 0.5, t("overview.no_data_chart"),
                    ha='center', va='center', color='#7F8C8D', fontsize=11)
            ax.axis('off')
            self.overview_canvas.draw()
            return

        # 1) VOC Kano type distribution
        ax1 = self.overview_fig.add_subplot(131)
        ax1.set_aspect('equal')  # keep the pie circular even if the canvas gets stretched wide
        kano_colors = {'M': '#F1948A', 'O': '#7FB3E8', 'A': '#82E0AA',
                       'I': '#CACFD2', 'R': '#F8C471', '': '#D5DBDB'}
        counts = {}
        for v in vocs:
            k = v.get('kano_type') or ''
            counts[k] = counts.get(k, 0) + 1
        if counts:
            labels = [t(KANO_TYPE_KEYS.get(k, 'kano.unclassified')).split(' ')[0] for k in counts]
            sizes = list(counts.values())
            colors = [kano_colors.get(k, '#BDC3C7') for k in counts]
            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.0f%%',
                    textprops={'fontsize': 8})
        else:
            ax1.text(0.5, 0.5, t("overview.no_voc_chart"), ha='center', va='center', color='#7F8C8D')
            ax1.axis('off')
        ax1.set_title(t("overview.kano_dist"), fontsize=10, fontweight='bold')

        # 2) Top-5 VOC by HOQ right-wall priority (Wi)
        ax2 = self.overview_fig.add_subplot(132)
        if vocs:
            ranked = self._voc_priority_ranking(vocs)[:5]
            names = [n for n, _ in ranked][::-1]
            vals = [w for _, w in ranked][::-1]
            ax2.barh(names, vals, color='#58D68D')
            ax2.tick_params(axis='y', labelsize=8)
        else:
            ax2.text(0.5, 0.5, t("overview.no_voc_chart"), ha='center', va='center', color='#7F8C8D', fontsize=9)
            ax2.axis('off')
        ax2.set_title(t("overview.top5_voc"), fontsize=10, fontweight='bold')

        # 3) Top-5 CTQ by absolute technical importance (Tai, from the floor)
        ax3 = self.overview_fig.add_subplot(133)
        if ctqs and rels:
            importance = HOQEngine.compute_importance(vocs, ctqs, rels)
            ranked = sorted(ctqs,
                             key=lambda c: importance.get(c['id'], {}).get('absolute_importance', 0),
                             reverse=True)[:5]
            names = [c['name'] for c in ranked][::-1]
            vals = [importance.get(c['id'], {}).get('absolute_importance', 0) for c in ranked][::-1]
            ax3.barh(names, vals, color=COLORS['rel_medium'])
            ax3.tick_params(axis='y', labelsize=8)
        else:
            ax3.text(0.5, 0.5, t("overview.no_rel_chart"),
                    ha='center', va='center', color='#7F8C8D', fontsize=9)
            ax3.axis('off')
        ax3.set_title(t("overview.top5_ctq"), fontsize=10, fontweight='bold')

        self.overview_fig.tight_layout()
        self.overview_canvas.draw()

    def _update_readiness(self, vocs, ctqs, rels, comps):
        checks = [
            (len(vocs) > 0, t("readiness.voc", n=len(vocs))),
            (len(ctqs) > 0, t("readiness.ctq", n=len(ctqs))),
            (len(rels) > 0, t("readiness.rel", n=len(rels))),
            (len(comps) > 0, t("readiness.comp", n=len(comps))),
        ]
        lines = []
        for ok, text in checks:
            icon, color = ("✅", "#27AE60") if ok else ("⭕", "#BDC3C7")
            lines.append(f"<span style='color:{color};'>{icon} {text}</span>")
        self.readiness_label.setText("<br/>".join(lines))

    def _auto_save(self):
        if self.project_id:
            self.db.update_project(self.project_id)
            self.statusBar().showMessage(t("msg.auto_saved"), 3000)

    def closeEvent(self, event):
        if self.project_id:
            self.db.save_version(self.project_id, t("msg.auto_save_version"))
        self.db.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(build_main_stylesheet(os.path.join(_APP_DIR, "assets")))
    app.setStyle("Fusion")

    # Set app icon (shows in taskbar on all platforms)
    icon_path = os.path.join(_APP_DIR, "assets", "qfd.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        png_path = os.path.join(_APP_DIR, "assets", "icon_256.png")
        if os.path.exists(png_path):
            app.setWindowIcon(QIcon(png_path))

    # Windows taskbar: set AppUserModelID so icon shows correctly
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("OpenQFD.1.0")
        except Exception:
            pass

    font = QFont("Microsoft YaHei", 9)
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)

    if not load_settings().get('license_agreed'):
        gate = StartupGateDialog()
        if gate.exec() != QDialog.Accepted:
            sys.exit(0)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
