from PySide6.QtWidgets import QGraphicsView, QGraphicsEllipseItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor

from utils.coordinate_utils import to_centered_coordinates


class GridView(QGraphicsView):
    def __init__(self, scene, grid_page):
        super().__init__(scene)
        self.grid_page = grid_page
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        pos = self.mapToScene(event.pos())

        width = self.grid_page.state.cam_res_x
        height = self.grid_page.state.cam_res_y

        # 🔒 Ignore hover outside grid
        if not (0 <= pos.x() <= width and 0 <= pos.y() <= height):
            self.grid_page.coord_label.setText("Hover: (-, -)")
            return

        x, y = to_centered_coordinates(
            pos.x(),
            pos.y(),
            width,
            height
        )

        self.grid_page.coord_label.setText(f"Hover: ({x}, {y}) px")

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        pos = self.mapToScene(event.pos())

        width = self.grid_page.state.cam_res_x
        height = self.grid_page.state.cam_res_y

        # 🔒 Ignore clicks outside grid
        if not (0 <= pos.x() <= width and 0 <= pos.y() <= height):
            return

        # Enforce click limit
        if len(self.grid_page.state.clicked_points) >= self.grid_page.max_clicks:
            return

        x, y = to_centered_coordinates(
            pos.x(),
            pos.y(),
            width,
            height
        )

        # Store point
        self.grid_page.state.clicked_points.append((x, y))

        # Draw marker
        self.draw_point_marker(pos.x(), pos.y())

        # Update list
        self.grid_page.update_point_list()

        super().mousePressEvent(event)

    def draw_point_marker(self, scene_x, scene_y):
        radius = max(
            self.grid_page.state.cam_res_x,
            self.grid_page.state.cam_res_y
        ) * 0.005

        point = QGraphicsEllipseItem(
            scene_x - radius,
            scene_y - radius,
            radius * 2,
            radius * 2
        )

        point.setBrush(QBrush(QColor(0, 255, 0)))
        point.setZValue(10)

        self.scene().addItem(point)