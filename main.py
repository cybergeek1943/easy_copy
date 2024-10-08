from core import settings_data
from core.settings_data import CustomSettings
from core.translation import tr, init_translator
from core.config import user_docs_path
import core.importer_exporter as importer_exporter
import process_manager
import process_manager_ui
import settings_ui

# Import Components and Visual Tools
from qfluentwidgets import BodyLabel, PrimaryPushButton, PushButton, ProgressBar
from ui_comps import AlignFlag, SizePolicy, Icons, primitives, windows, dialogs
from PySide6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QGridLayout, QFileDialog
from PySide6.QtCore import QTimer
from qfluentwidgets import NavigationItemPosition
from core.asset_paths import MainIconPaths


class builders:
    class VisualConnectorLine(ProgressBar):
        def __init__(self):
            super().__init__()
            self.setMinimumHeight(6)
            self.setMinimumWidth(200)
            self.setCustomBarColor('#73e68c', '#73e68c')

        def set_complete(self, b: bool):
            self.setValue(100 if b else 0)

    class PrimaryButton(PrimaryPushButton):
        def __init__(self, label: str, slots: tuple[callable] = None, disabled: bool = True):
            super().__init__()
            if slots:
                for c in slots:
                    self.clicked.connect(c)
            self.setText(label)
            self.setMinimumWidth(170)
            # applyAdditionalStyleSheet(self, 'QPushButton {border-radius: 10px;}')
            self.setDisabled(disabled)

    class Button(PushButton):
        def __init__(self, icon: Icons, label: str, tooltip: str, slots: tuple[callable] = None, disabled: bool = False):
            super().__init__()
            if slots:
                for c in slots:
                    self.clicked.connect(c)
            self.setIcon(icon)
            self.setText(label)
            self.setToolTip(tooltip)
            self.setDisabled(disabled)
            self.setSizePolicy(SizePolicy.Fixed, SizePolicy.Fixed)


class HomeTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('home_tab')
        v_lay = QVBoxLayout()
        self.setLayout(v_lay)
        v_lay.addWidget(primitives.ImageIcon(MainIconPaths.logoWName, 32), alignment=AlignFlag.AlignHCenter)

        # -------- UI --------
        ui = QWidget()
        ui.setSizePolicy(SizePolicy.Fixed, SizePolicy.Fixed)
        v_lay.addWidget(ui, alignment=AlignFlag.AlignCenter)
        grid = QGridLayout()
        ui.setLayout(grid)

        # source
        from source_selection_ui import MainWindow as SourceSelectionSubWindow
        self.source_selection_sub_window = SourceSelectionSubWindow()
        QTimer.singleShot(100, lambda: (self.source_selection_sub_window.resize(int(self.window().size().width() * 0.9), int(self.window().size().height() * 0.9)),
                                        self.source_selection_sub_window.move(self.window().pos().x() + 32, self.window().pos().y() + 32)))  # we must use timer here because we need to wait for the main window to load.
        self.source_selection_sub_window.windowClosing.connect(lambda: self.on_source_selection_window_closed(self.source_selection_sub_window.selection_manager_tab.widget_count()))
        grid.addWidget(primitives.ImageIcon(MainIconPaths.selectSource), 0, 0, alignment=AlignFlag.AlignCenter)
        self.select_source_button = builders.PrimaryButton(tr('Select Source'), slots=(self.source_selection_sub_window.show,), disabled=False)
        grid.addWidget(self.select_source_button, 2, 0, alignment=AlignFlag.AlignCenter)
        self.source_connector_line = builders.VisualConnectorLine()
        grid.addWidget(self.source_connector_line, 0, 1, alignment=AlignFlag.AlignCenter)

        # destination
        from destination_selection_ui import MainWindow as DestinationSelectionWindow
        self.destination_selection_sub_window = DestinationSelectionWindow()
        QTimer.singleShot(100, lambda: (self.destination_selection_sub_window.resize(int(self.window().size().width() * 0.9), int(self.window().size().height() * 0.9)),
                                        self.destination_selection_sub_window.move(self.window().pos().x() + 32, self.window().pos().y() + 32)))  # we must use timer here because we need to wait for the main window to load.
        self.destination_selection_sub_window.windowClosing.connect(lambda: self.on_destination_selection_window_closed(self.destination_selection_sub_window.selection_manager_tab.widget_count()))
        grid.addWidget(primitives.ImageIcon(MainIconPaths.selectDestination), 0, 2, alignment=AlignFlag.AlignCenter)
        self.select_destination_button = builders.PrimaryButton(tr('Select Destination'), slots=(self.destination_selection_sub_window.show,))
        grid.addWidget(self.select_destination_button, 2, 2, alignment=AlignFlag.AlignCenter)
        self.destination_connector_line = builders.VisualConnectorLine()
        grid.addWidget(self.destination_connector_line, 0, 3, alignment=AlignFlag.AlignCenter)

        # start copy
        grid.addWidget(primitives.ImageIcon(MainIconPaths.startCopy), 0, 4, alignment=AlignFlag.AlignCenter)
        self.start_copy_button = builders.PrimaryButton(tr('Start Copy'), slots=(self.on_start_copy_pressed,))
        grid.addWidget(self.start_copy_button, 2, 4, alignment=AlignFlag.AlignCenter)

        # spacers
        grid.addWidget(primitives.SpacerItem(0, 32), 1, 2)  # vertical space between buttons and icons.
        grid.addWidget(primitives.SpacerItem(0, 32), 3, 2)  # vertical space after buttons to shift ui up.

    def on_source_selection_window_closed(self, selected_file_count: int):
        if selected_file_count == 0:
            self.select_destination_button.setDisabled(True)
            self.start_copy_button.setDisabled(True)
            self.source_connector_line.set_complete(False)
            self.destination_connector_line.set_complete(False)
            return
        self.select_destination_button.setDisabled(False)
        self.source_connector_line.set_complete(True)

    def on_destination_selection_window_closed(self, selected_folder_count: int):
        if selected_folder_count == 0:
            self.start_copy_button.setDisabled(True)
            self.destination_connector_line.set_complete(False)
            return
        self.start_copy_button.setDisabled(False)
        self.destination_connector_line.set_complete(True)

    def on_start_copy_pressed(self):
        source_selection: list[tuple[str, dict]] = self.source_selection_sub_window.get_source_selection()
        destination_selection: list[str] = self.destination_selection_sub_window.get_destination_selection()
        process_manager.init_processes(source_selection, destination_selection)
        self.window().hide()
        if CustomSettings.use_gui:
            process_manager_ui.start(app_context=app)
        else:
            process_manager.start_all_processes()

class JobTab(QWidget):
    def __init__(self, home_tab: HomeTab):
        super().__init__()
        self.home_tab = home_tab
        self.setObjectName('job_tab')
        v_lay = QVBoxLayout()
        v_lay.setAlignment(AlignFlag.AlignTop)
        self.setLayout(v_lay)

        # -------- UI --------
        _ = BodyLabel()
        _.setText(tr('<h2>Job Manager</h2>'
                     'You may create and utilize job files to execute regularly required copy operations.<br/>'))
        v_lay.addWidget(_)
        buttons_lay = QHBoxLayout()
        buttons_lay.setAlignment(AlignFlag.AlignLeft)
        v_lay.addLayout(buttons_lay)
        buttons_lay.addWidget(builders.Button(Icons.SAVE_AS, tr('Create a Job File'), tr('Create a (*.job) file from the current selection of sources, destinations, and settings.'), slots=(self.create_job_file,)))
        buttons_lay.addWidget(builders.Button(Icons.PLAY, tr('Run a Job File'), tr('Run a (*.job) file containing sources, destinations, and settings.'), slots=(self.run_job_file,)))

    def run_job_file(self):
        if (path := QFileDialog.getOpenFileName(self, tr('Run a Job File'), user_docs_path, tr('Jobs (*.job)')))[0]:
            if j := importer_exporter.import_job_file(path[0]):
                process_manager.init_processes(*j)
                self.window().hide()
                if CustomSettings.use_gui:
                    process_manager_ui.start(app_context=app)
                else:
                    app.quit()
                    process_manager.start_all_processes()
            else:
                dialogs.info(self, tr('Error'), tr('This file could not be imported because it is corrupt!'), critical=True)

    def create_job_file(self):
        source_selection: list[tuple[str, dict]] = self.home_tab.source_selection_sub_window.get_source_selection()
        destination_selection: list[str] = self.home_tab.destination_selection_sub_window.get_destination_selection()
        if not source_selection or not destination_selection:
            dialogs.info(self, tr('Cannot Create Job File'), tr('Please select both a source and destination before you create job files!'), critical=True)
            return
        if (path := QFileDialog.getSaveFileName(self, tr('Create a Job File'), f'{user_docs_path}/main', tr('Jobs (*.job)')))[0]:
            importer_exporter.export_job_file(path[0], source_selection, destination_selection)


class MainWindow(windows.TabWindow):
    def __init__(self):
        super().__init__(remember_window_pos=False, menu_expand_width=150)
        self.setWindowTitle(tr('VisiCopy'))
        self.resize(1370, 700)
        self.navigationInterface.setCollapsible(True)
        self.navigationInterface.setReturnButtonVisible(False)

        # -------------------------------- Tabs --------------------------------
        # src/dst selection
        home_tab = HomeTab()
        self.addSubInterface(home_tab, Icons.HOME, tr('Home'))

        # Job Manager
        self.addSubInterface(JobTab(home_tab), Icons.BOOK_SHELF, tr('Job Manager'))

        # Settings Button
        self.navigationInterface.addItem('open_settings', Icons.SETTING, tr('Settings'), selectable=False, onClick=settings_ui.start, position=NavigationItemPosition.BOTTOM)

    def closeEvent(self, event):
        app.exit()
        event.ignore()  # so that dialog cancel button can work


class Application(QApplication):
    def exit(self, retcode: int = 0, force_exit: bool = False):
        if not force_exit and settings_data.changes_detected != 0:
            title: str = tr('Confirm Change')
            message: str = tr('You made 1 change in the settings.\nDo you want to save this change for future use?') if settings_data.changes_detected == 1 \
                else tr('You made {} changes in the settings.\nDo you want to save these changes for future use?').format(settings_data.changes_detected)
            r = dialogs.question(main_window, title, message, show_cancel_button=True)
            if r == dialogs.response.Yes:
                settings_data.save_settings()
            elif r == dialogs.response.Cancel:
                return
        settings_data.set_detected_changes(0)
        super().exit(retcode)


app: Application = Application()
init_translator(app)
main_window: MainWindow
def start():
    global main_window
    main_window = MainWindow()
    main_window.show()
    settings_ui.app = app
    app.exec()  # loop starts here and only exits when application is quit or restarted


if __name__ == '__main__':  # pyside6-deploy main.py
    start()
