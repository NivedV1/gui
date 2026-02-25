from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QProgressBar
)
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QImage, QPixmap

import numpy as np

from core.gs_algorithm import (
    gaussian_beam,
    traps_to_target,
    gerchberg_saxton
)


class ExperimentPage(QWidget):
    def __init__(self, state, go_back_callback):
        super().__init__()
        self.state = state
        self.go_back = go_back_callback
        self.current_view = "source"

        main_layout = QHBoxLayout()

        # LEFT PANEL
        self.left_box = QFrame()
        self.left_box.setFrameShape(QFrame.Box)
        left_layout = QVBoxLayout()

        self.left_label = QLabel("Source Intensity")
        self.left_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.left_label)

        left_layout.addStretch()

        self.switch_button = QPushButton("Switch to Target")
        self.switch_button.clicked.connect(self.switch_view)
        left_layout.addWidget(self.switch_button)

        self.left_box.setLayout(left_layout)

        # RIGHT PANEL
        self.right_box = QFrame()
        self.right_box.setFrameShape(QFrame.Box)
        right_layout = QVBoxLayout()

        self.phase_label = QLabel("Phase Map (SLM)")
        self.phase_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.phase_label)

        self.run_button = QPushButton("Run GS Algorithm")
        self.run_button.clicked.connect(self.run_gs)
        right_layout.addWidget(self.run_button)

        self.right_box.setLayout(right_layout)

        main_layout.addWidget(self.left_box)
        main_layout.addWidget(self.right_box)

        # BOTTOM CONTROLS
        bottom_layout = QHBoxLayout()

        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.go_back_and_clear)
        bottom_layout.addWidget(self.back_button)

        bottom_layout.addStretch()

        self.progress = QProgressBar()
        self.progress.setValue(0)
        bottom_layout.addWidget(self.progress)

        wrapper = QVBoxLayout()
        wrapper.addLayout(main_layout)
        wrapper.addLayout(bottom_layout)

        self.setLayout(wrapper)

        self.source_img = None
        self.target_img = None

    def switch_view(self):
        if self.current_view == "source":
            self.current_view = "target"
            self.left_label.setText("Target Intensity")
            self.switch_button.setText("Switch to Source")
            if self.target_img is not None:
                self.show_image(self.target_img, self.left_label)
        else:
            self.current_view = "source"
            self.left_label.setText("Source Intensity")
            self.switch_button.setText("Switch to Target")
            if self.source_img is not None:
                self.show_image(self.source_img, self.left_label)

    def go_back_and_clear(self):
        self.source_img = None
        self.target_img = None
        self.left_label.clear()
        self.phase_label.clear()
        self.progress.setValue(0)
        self.go_back()

    def run_gs(self):

        nx = self.state.slm_res_x
        ny = self.state.slm_res_y

        source = gaussian_beam(nx, ny)
        traps = self.state.clicked_points

        if not traps:
            print("No traps selected!")
            return

        target = traps_to_target(traps, nx, ny)

        iterations = 80
        self.progress.setValue(0)

        phase = np.exp(1j * 2 * np.pi * np.random.rand(ny, nx))
        field = source * phase

        for i in range(iterations):
            target_field = np.fft.fftshift(np.fft.fft2(field))
            target_field = target * np.exp(1j * np.angle(target_field))
            field = np.fft.ifft2(np.fft.ifftshift(target_field))
            field = source * np.exp(1j * np.angle(field))

            percent = int((i + 1) / iterations * 100)
            self.progress.setValue(percent)
            QCoreApplication.processEvents()

        phase_map = np.angle(field)

        self.source_img = source
        self.target_img = target

        if self.current_view == "source":
            self.show_image(source, self.left_label)
        else:
            self.show_image(target, self.left_label)

        self.show_phase(phase_map, self.phase_label)

        self.progress.setValue(100)

    def show_image(self, img, label):
        img8 = (img * 255).astype(np.uint8)
        h, w = img8.shape
        qimg = QImage(img8.data, w, h, w, QImage.Format_Grayscale8)
        label.setPixmap(QPixmap.fromImage(qimg).scaled(420, 420, Qt.KeepAspectRatio))

    def show_phase(self, phase, label):
        phase_norm = (phase + np.pi) / (2 * np.pi)
        img8 = (phase_norm * 255).astype(np.uint8)
        h, w = img8.shape
        qimg = QImage(img8.data, w, h, w, QImage.Format_Grayscale8)
        label.setPixmap(QPixmap.fromImage(qimg).scaled(420, 420, Qt.KeepAspectRatio))