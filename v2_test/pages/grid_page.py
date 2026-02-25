from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QGraphicsScene, QSpinBox,
    QPushButton, QHBoxLayout, QLineEdit
)
from PySide6.QtGui import QPen, QColor
from PySide6.QtCore import Qt

from widgets.grid_view import GridView


class GridPage(QWidget):
    def __init__(self, state, go_next_callback, go_back_callback):
        super().__init__()
        self.state = state
        self.go_next = go_next_callback
        self.go_back = go_back_callback
        self.max_clicks = 1

        main_layout = QVBoxLayout()

        main_layout.addWidget(QLabel("Number of Clicks:"))

        self.click_selector = QSpinBox()
        self.click_selector.setRange(1, 100)
        self.click_selector.setValue(1)
        self.click_selector.valueChanged.connect(self.update_click_limit)
        main_layout.addWidget(self.click_selector)

        # buttons row
        btn_row = QHBoxLayout()

        self.undo_button = QPushButton("Undo Last")
        self.undo_button.clicked.connect(self.undo_last_point)
        btn_row.addWidget(self.undo_button)

        self.clear_button = QPushButton("Clear Points")
        self.clear_button.clicked.connect(self.clear_points)
        btn_row.addWidget(self.clear_button)

        main_layout.addLayout(btn_row)

        self.coord_label = QLabel("Hover: (-, -)")
        main_layout.addWidget(self.coord_label)

        self.scene = QGraphicsScene()
        self.view = GridView(self.scene, self)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        main_layout.addWidget(self.view)

        main_layout.addWidget(QLabel("Clicked Points (Editable):"))

        self.points_edit = QLineEdit()
        self.points_edit.returnPressed.connect(self.apply_manual_points)
        main_layout.addWidget(self.points_edit)

        # navigation
        nav = QHBoxLayout()

        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.go_back_and_clear)
        nav.addWidget(self.back_button)

        nav.addStretch()

        self.next_button = QPushButton("Next →")
        self.next_button.clicked.connect(self.go_next)
        nav.addWidget(self.next_button)

        main_layout.addLayout(nav)

        self.setLayout(main_layout)
        self.initialize_grid()

    # ---------------------
    # logic
    # ---------------------

    def update_click_limit(self):
        self.max_clicks = self.click_selector.value()

    def update_point_list(self):
        self.points_edit.setText(str(self.state.clicked_points))

    def undo_last_point(self):
        if self.state.clicked_points:
            self.state.clicked_points.pop()
            self.redraw_points()

    def clear_points(self):
        self.state.clicked_points.clear()
        self.redraw_points()

    def go_back_and_clear(self):
        self.state.clicked_points.clear()
        self.go_back()

    def apply_manual_points(self):
        text = self.points_edit.text().strip()
        try:
            pts = eval(text)
            validated = []
            for p in pts:
                if isinstance(p, (list, tuple)) and len(p) == 2:
                    validated.append((int(p[0]), int(p[1])))
            self.state.clicked_points = validated
            self.redraw_points()
        except:
            print("Invalid format: use [(x1,y1),(x2,y2)]")

    # ---------------------
    # drawing
    # ---------------------

    def initialize_grid(self):
        self.redraw_points()

    def redraw_points(self):
        self.scene.clear()

        w = self.state.cam_res_x
        h = self.state.cam_res_y
        self.scene.setSceneRect(0, 0, w, h)

        # border
        pen = QPen(Qt.white)
        pen.setWidth(2)
        self.scene.addRect(0, 0, w, h, pen)

        cx, cy = w/2, h/2

        # center lines
        red = QPen(Qt.red)
        red.setWidth(2)
        self.scene.addLine(cx, 0, cx, h, red)
        self.scene.addLine(0, cy, w, cy, red)

        # draw stored points
        for gx, gy in self.state.clicked_points:
            px = cx + gx
            py = cy - gy
            r = 5
            self.scene.addEllipse(px-r, py-r, 2*r, 2*r,
                                  QPen(Qt.green), QColor(0,255,0))

        self.update_point_list()
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)