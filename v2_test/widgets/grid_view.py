from PySide6.QtWidgets import QGraphicsView, QGraphicsEllipseItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor

from utils.coordinate_utils import to_centered_coordinates


class GridView(QGraphicsView):
    def __init__(self, scene, grid_page):
        super().__init__(scene)
        self.grid_page = grid_page
        self.setMouseTracking(True)

        self.dragging_point = None
        self.drag_index = None

    # ------------------------
    # Hover coordinates
    # ------------------------
    def mouseMoveEvent(self, event):
        pos = self.mapToScene(event.pos())

        width = self.grid_page.state.cam_res_x
        height = self.grid_page.state.cam_res_y

        if not (0 <= pos.x() <= width and 0 <= pos.y() <= height):
            self.grid_page.coord_label.setText("Hover: (-, -)")
            return

        x, y = to_centered_coordinates(
            pos.x(), pos.y(), width, height
        )

        self.grid_page.coord_label.setText(f"Hover: ({x}, {y}) px")

        # drag selected point
        if self.dragging_point is not None:
            self.dragging_point.setPos(pos.x() - 5, pos.y() - 5)

        super().mouseMoveEvent(event)

    # ------------------------
    # Click to add/select
    # ------------------------
    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        pos = self.mapToScene(event.pos())

        width = self.grid_page.state.cam_res_x
        height = self.grid_page.state.cam_res_y

        if not (0 <= pos.x() <= width and 0 <= pos.y() <= height):
            return

        # check if clicking existing marker
        items = self.scene().items(pos)
        for item in items:
            if isinstance(item, QGraphicsEllipseItem):
                self.dragging_point = item
                self.drag_index = item.data(0)
                return

        # limit clicks
        if len(self.grid_page.state.clicked_points) >= self.grid_page.max_clicks:
            return

        x, y = to_centered_coordinates(
            pos.x(), pos.y(), width, height
        )

        self.grid_page.state.clicked_points.append((x, y))

        self.draw_marker_from_center(x, y)
        self.grid_page.update_point_list()

        super().mousePressEvent(event)

    # ------------------------
    # Release to update position
    # ------------------------
    def mouseReleaseEvent(self, event):
        if self.dragging_point is not None:
            pos = self.mapToScene(event.pos())

            width = self.grid_page.state.cam_res_x
            height = self.grid_page.state.cam_res_y

            x, y = to_centered_coordinates(
                pos.x(), pos.y(), width, height
            )

            # update stored coordinate
            self.grid_page.state.clicked_points[self.drag_index] = (x, y)
            self.grid_page.update_point_list()

            self.dragging_point = None
            self.drag_index = None

        super().mouseReleaseEvent(event)

    # ------------------------
    # Draw marker from centered coords
    # ------------------------
    def draw_marker_from_center(self, x, y):
        width = self.grid_page.state.cam_res_x
        height = self.grid_page.state.cam_res_y

        cx = width / 2
        cy = height / 2

        scene_x = cx + x
        scene_y = cy - y

        radius = max(width, height) * 0.005

        point = QGraphicsEllipseItem(
            scene_x - radius,
            scene_y - radius,
            radius * 2,
            radius * 2
        )

        point.setBrush(QBrush(QColor(0, 255, 0)))
        point.setZValue(10)

        # store index for editing
        point.setData(0, len(self.grid_page.state.clicked_points) - 1)

        self.scene().addItem(point)