from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt


class ExperimentPage(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.current_mode = "Source"

        main_layout = QHBoxLayout()

        # ----------------
        # Left Box (Camera)
        # ----------------
        self.left_box = QFrame()
        self.left_box.setFrameShape(QFrame.Box)
        left_layout = QVBoxLayout()

        self.camera_label = QLabel("Camera Output: Source")
        self.camera_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.camera_label)

        left_layout.addStretch()

        self.switch_button = QPushButton("Switch to Target")
        self.switch_button.clicked.connect(self.switch_camera_mode)
        left_layout.addWidget(self.switch_button)

        self.left_box.setLayout(left_layout)

        # ----------------
        # Right Box (Hologram)
        # ----------------
        self.right_box = QFrame()
        self.right_box.setFrameShape(QFrame.Box)
        right_layout = QVBoxLayout()

        self.hologram_label = QLabel("Hologram Output (GS Algorithm)")
        self.hologram_label.setAlignment(Qt.AlignCenter)

        right_layout.addWidget(self.hologram_label)
        self.right_box.setLayout(right_layout)

        # Add both to main layout
        main_layout.addWidget(self.left_box)
        main_layout.addWidget(self.right_box)

        self.setLayout(main_layout)

    def switch_camera_mode(self):
        if self.current_mode == "Source":
            self.current_mode = "Target"
            self.camera_label.setText("Camera Output: Target")
            self.switch_button.setText("Switch to Source")
        else:
            self.current_mode = "Source"
            self.camera_label.setText("Camera Output: Source")
            self.switch_button.setText("Switch to Target")