import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from core.app_state import AppState
from pages.parameter_page import ParameterPage
from pages.grid_page import GridPage
from pages.experiment_page import ExperimentPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optical Tweezers App")

        self.state = AppState()

        self.stack = QStackedWidget()

        self.parameter_page = ParameterPage(
            self.state,
            self.go_to_grid
        )

        # ✅ pass BOTH callbacks
        self.grid_page = GridPage(
            self.state,
            self.go_to_experiment,
            self.go_to_parameter
        )

        self.experiment_page = ExperimentPage(
            self.state,
            self.go_to_grid
        )

        self.stack.addWidget(self.parameter_page)
        self.stack.addWidget(self.grid_page)
        self.stack.addWidget(self.experiment_page)

        self.setCentralWidget(self.stack)

    def go_to_parameter(self):
        self.stack.setCurrentIndex(0)

    def go_to_grid(self):
        self.grid_page.initialize_grid()
        self.stack.setCurrentIndex(1)

    def go_to_experiment(self):
        self.stack.setCurrentIndex(2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec())