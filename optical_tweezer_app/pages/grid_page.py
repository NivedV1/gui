from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QGraphicsScene, QSpinBox,
    QPushButton, QHBoxLayout
)
from PySide6.QtGui import QPen, QColor
from PySide6.QtCore import Qt

from widgets.grid_view import GridView


class GridPage(QWidget):
    def __init__(self, state, go_next_callback):
        super().__init__()
        self.state = state
        self.go_next = go_next_callback
        self.max_clicks = 1

        main_layout = QVBoxLayout()

        # Click selector
        main_layout.addWidget(QLabel("Number of Clicks:"))

        self.click_selector = QSpinBox()
        self.click_selector.setRange(1, 100)
        self.click_selector.setValue(1)
        self.click_selector.valueChanged.connect(self.update_click_limit)
        main_layout.addWidget(self.click_selector)

        self.clear_button = QPushButton("Clear Points")
        self.clear_button.clicked.connect(self.clear_points)
        main_layout.addWidget(self.clear_button)

        self.coord_label = QLabel("Hover: (-, -)")
        main_layout.addWidget(self.coord_label)

        # Graphics
        self.scene = QGraphicsScene()
        self.view = GridView(self.scene, self)

        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        main_layout.addWidget(self.view)

        self.points_label = QLabel("Clicked Points: []")
        main_layout.addWidget(self.points_label)

        # Bottom layout for next button (right aligned)
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self.next_button = QPushButton("Next →")
        self.next_button.clicked.connect(self.go_next)
        bottom_layout.addWidget(self.next_button)

        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    # ----------------
    # Click logic
    # ----------------

    def update_click_limit(self):
        self.max_clicks = self.click_selector.value()

    def clear_points(self):
        self.state.clicked_points = []
        self.initialize_grid()

    def update_point_list(self):
        self.points_label.setText(
            f"Clicked Points: {self.state.clicked_points}"
        )

    # ----------------
    # Grid drawing
    # ----------------

    def initialize_grid(self):
        self.scene.clear()
        self.state.clicked_points = []
        self.update_point_list()

        width = self.state.cam_res_x
        height = self.state.cam_res_y

        self.scene.setSceneRect(0, 0, width, height)

        box_pen = QPen(Qt.white)
        box_pen.setWidth(2)
        self.scene.addRect(0, 0, width, height, box_pen)

        grid_spacing = 128
        grid_pen = QPen(QColor(150, 150, 150, 80))

        center_x = width / 2
        center_y = height / 2

        x = center_x
        while x <= width:
            self.scene.addLine(x, 0, x, height, grid_pen)
            x += grid_spacing

        x = center_x - grid_spacing
        while x >= 0:
            self.scene.addLine(x, 0, x, height, grid_pen)
            x -= grid_spacing

        y = center_y
        while y <= height:
            self.scene.addLine(0, y, width, y, grid_pen)
            y += grid_spacing

        y = center_y - grid_spacing
        while y >= 0:
            self.scene.addLine(0, y, width, y, grid_pen)
            y -= grid_spacing

        center_pen = QPen(Qt.red)
        center_pen.setWidth(2)
        self.scene.addLine(center_x, 0, center_x, height, center_pen)
        self.scene.addLine(0, center_y, width, center_y, center_pen)

        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        if self.scene.sceneRect().width() > 0:
            self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        super().resizeEvent(event)