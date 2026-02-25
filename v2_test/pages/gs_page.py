from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt

import numpy as np

from core.gs_algorithm import (
    gaussian_beam,
    simple_target,
    gerchberg_saxton
)


class GSPage(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state

        layout = QVBoxLayout()

        self.title = QLabel("Gerchberg–Saxton Output")
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        self.image_label = QLabel("Press button to run GS")
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        self.run_button = QPushButton("Run GS Algorithm")
        self.run_button.clicked.connect(self.run_gs)
        layout.addWidget(self.run_button)

        self.setLayout(layout)

    def run_gs(self):
        nx = self.app_state.slm_res_x
        ny = self.app_state.slm_res_y

        source = gaussian_beam(nx, ny)
        target = simple_target(nx, ny)

        result = gerchberg_saxton(source, target, iterations=60)

        self.display_image(result)

    def display_image(self, img):
        img8 = (img * 255).astype(np.uint8)
        h, w = img8.shape

        qimg = QImage(img8.data, w, h, w, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimg)

        self.image_label.setPixmap(
            pixmap.scaled(420, 420, Qt.KeepAspectRatio)
        )