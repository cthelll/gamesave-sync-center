from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QToolBar,
    QVBoxLayout,
    QWidget,
)


ROOT = Path(__file__).resolve().parent
QSS_FILE = Path(__file__).resolve().with_name("gnome_hig.qss")


def _load_qss() -> str:
    try:
        return QSS_FILE.read_text(encoding="utf-8")
    except Exception:
        return ""


def _button_by_text(window, names):
    wanted = {x.replace("&", "").strip().lower() for x in names}
    for button in window.findChildren(QPushButton):
        text = button.text().replace("&", "").strip().lower()
        if text in wanted:
            return button
    return None


def _attr(window, names):
    for name in names:
        widget = getattr(window, name, None)
        if widget is not None:
            return widget
    return None


def _label(text: str) -> QLabel:
    label = QLabel(text)
    label.setAlignment(Qt.AlignVCenter)
    return label


def _prepare_combo(combo: QComboBox | None, minimum: int, maximum: int | None = None):
    if combo is None:
        return
    combo.setVisible(True)
    combo.setMinimumWidth(minimum)
    if maximum:
        combo.setMaximumWidth(maximum)
    combo.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)


def _prepare_line(line: QLineEdit | None):
    if line is None:
        return
    line.setVisible(True)
    line.setMinimumWidth(480)
    line.setMaximumWidth(920)
    line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


def _prepare_button(button: QPushButton | None, minimum: int | None = None):
    if button is None:
        return
    button.setVisible(True)
    if minimum:
        button.setMinimumWidth(minimum)
    button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)


def _detach_from_toolbars(window, widgets):
    widget_set = {w for w in widgets if w is not None}

    for toolbar in window.findChildren(QToolBar):
        for action in list(toolbar.actions()):
            widget = None
            try:
                widget = toolbar.widgetForAction(action)
            except Exception:
                widget = None

            if widget in widget_set:
                toolbar.removeAction(action)
                widget.setVisible(True)

        toolbar.hide()


def _remove_old_panels(window):
    for name in ["gnomeTopPanel", "normalTopPanel"]:
        while True:
            old = window.findChild(QWidget, name)
            if old is None:
                break
            old.setParent(None)
            old.deleteLater()


def _browser_like_size(window):
    window.setMinimumSize(1220, 760)

    screen = QApplication.primaryScreen()
    if not screen:
        window.resize(1480, 880)
        return

    area = screen.availableGeometry()
    width = min(1720, max(1360, int(area.width() * 0.92)))
    height = min(1000, max(820, int(area.height() * 0.88)))

    window.resize(width, height)
    window.move(
        area.x() + (area.width() - width) // 2,
        area.y() + (area.height() - height) // 2,
    )


def _force_rescan_connection(window, rescan_btn):
    if rescan_btn is None:
        return

    rescan = getattr(window, "rescan", None)
    if not callable(rescan):
        return

    try:
        rescan_btn.clicked.disconnect()
    except Exception:
        pass

    rescan_btn.clicked.connect(rescan)


def _force_filter_connections(window, view, sort, search):
    apply_filters = getattr(window, "apply_filters", None)

    if callable(apply_filters):
        if view is not None:
            try:
                view.currentTextChanged.disconnect()
            except Exception:
                pass
            view.currentTextChanged.connect(lambda _x: apply_filters())

        if sort is not None:
                                                                                  
            handler = getattr(window, "_gss_sort_combo_changed", None)
            try:
                sort.currentTextChanged.disconnect()
            except Exception:
                pass
            sort.currentTextChanged.connect(lambda _x: apply_filters())

        if search is not None:
            try:
                search.textChanged.disconnect()
            except Exception:
                pass
            search.textChanged.connect(lambda _x: apply_filters())


def install_gnome_ui(window):
    window.setStyleSheet(_load_qss())

    central = window.centralWidget()
    if central is None or central.layout() is None:
        return

    _remove_old_panels(window)

    win_root = _attr(window, ["win_root_combo", "windows_root_combo"])
    user = _attr(window, ["user_combo", "windows_user_combo"])
    linux = _attr(window, ["linux_source_combo", "linux_combo"])
    view = _attr(window, ["view_combo"])
    sort = _attr(window, ["sort_combo"])
    search = _attr(window, ["search_input", "search_edit"])

    change_btn = (
        _attr(window, ["btn_choose_win_root", "btn_change_win_root", "btn_windows_disk"])
        or _button_by_text(window, ["Change...", "Change…", "Windows disk", "Choose..."])
    )

    add_source_btn = (
        _attr(window, ["btn_add_linux_root", "btn_add_source"])
        or _button_by_text(window, ["Add Source...", "Add Source…", "Add prefix/root"])
    )

    settings_btn = (
        _attr(window, ["btn_settings"])
        or _button_by_text(window, ["Settings", "Settings…"])
    )

    rescan_btn = (
        _attr(window, ["btn_rescan"])
        or _button_by_text(window, ["Rescan"])
    )

    widgets = [
        win_root,
        user,
        linux,
        view,
        sort,
        search,
        change_btn,
        add_source_btn,
        settings_btn,
        rescan_btn,
    ]

    _detach_from_toolbars(window, widgets)

    _prepare_line(search)
    _prepare_combo(win_root, 300, 520)
    _prepare_combo(user, 320, 560)
    _prepare_combo(linux, 300, 520)
    _prepare_combo(view, 140, 190)
    _prepare_combo(sort, 150, 220)

    _prepare_button(change_btn, 94)
    _prepare_button(add_source_btn, 116)
    _prepare_button(settings_btn, 104)
    _prepare_button(rescan_btn, 88)

    _force_rescan_connection(window, rescan_btn)
    _force_filter_connections(window, view, sort, search)

    panel = QFrame()
    panel.setObjectName("gnomeTopPanel")
    panel.setFrameShape(QFrame.NoFrame)

    panel_layout = QVBoxLayout(panel)
    panel_layout.setContentsMargins(12, 10, 12, 10)
    panel_layout.setSpacing(8)

    main_row = QHBoxLayout()
    main_row.setSpacing(8)

    main_row.addWidget(_label("Search"))
    if search:
        main_row.addWidget(search, 1)

    sources_btn = QPushButton("Sources ▾")
    sources_btn.setObjectName("sourcesButton")
    sources_btn.setMinimumWidth(106)
    main_row.addWidget(sources_btn)

    main_row.addSpacing(6)
    main_row.addWidget(_label("View"))
    if view:
        main_row.addWidget(view)

    main_row.addWidget(_label("Sort"))
    if sort:
        main_row.addWidget(sort)

    if rescan_btn:
        main_row.addSpacing(6)
        main_row.addWidget(rescan_btn)

    if settings_btn:
        main_row.addSpacing(6)
        main_row.addWidget(settings_btn)

    source_row_frame = QFrame()
    source_row_frame.setObjectName("sourceRow")
    source_row_frame.setVisible(False)

    source_row = QHBoxLayout(source_row_frame)
    source_row.setContentsMargins(10, 8, 10, 8)
    source_row.setSpacing(8)

    source_row.addWidget(_label("Windows"))
    if win_root:
        source_row.addWidget(win_root)
    if change_btn:
        source_row.addWidget(change_btn)

    source_row.addSpacing(10)
    source_row.addWidget(_label("User"))
    if user:
        source_row.addWidget(user)

    source_row.addSpacing(10)
    source_row.addWidget(_label("Linux"))
    if linux:
        source_row.addWidget(linux)

    if add_source_btn:
        source_row.addWidget(add_source_btn)

    source_row.addStretch(1)

    def toggle_sources():
        visible = not source_row_frame.isVisible()
        source_row_frame.setVisible(visible)
        sources_btn.setText("Sources ▴" if visible else "Sources ▾")

    sources_btn.clicked.connect(toggle_sources)

    panel_layout.addLayout(main_row)
    panel_layout.addWidget(source_row_frame)

    central.layout().insertWidget(0, panel)

    _browser_like_size(window)
