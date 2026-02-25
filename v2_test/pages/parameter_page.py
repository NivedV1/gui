from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout,
    QSpinBox, QDoubleSpinBox, QPushButton, QLabel
)


class ParameterPage(QWidget):
    def __init__(self, state, go_next_callback):
        super().__init__()
        self.state = state
        self.go_next = go_next_callback

        layout = QVBoxLayout()
        form = QFormLayout()

        # Camera
        self.cam_x = QSpinBox()
        self.cam_x.setRange(1, 10000)

        self.cam_y = QSpinBox()
        self.cam_y.setRange(1, 10000)

        self.cam_px = QDoubleSpinBox()
        self.cam_px.setDecimals(6)
        self.cam_px.setSuffix(" µm")

        # SLM
        self.slm_x = QSpinBox()
        self.slm_x.setRange(1, 10000)

        self.slm_y = QSpinBox()
        self.slm_y.setRange(1, 10000)

        self.slm_px = QDoubleSpinBox()
        self.slm_px.setDecimals(6)
        self.slm_px.setSuffix(" µm")

        form.addRow(QLabel("Camera Parameters"))
        form.addRow("Resolution X:", self.cam_x)
        form.addRow("Resolution Y:", self.cam_y)
        form.addRow("Pixel Size:", self.cam_px)

        form.addRow(QLabel("SLM Parameters"))
        form.addRow("Resolution X:", self.slm_x)
        form.addRow("Resolution Y:", self.slm_y)
        form.addRow("Pixel Size:", self.slm_px)

        layout.addLayout(form)

        # Buttons
        save_default_btn = QPushButton("Set Current Values as Default")
        save_default_btn.clicked.connect(self.save_as_default)
        layout.addWidget(save_default_btn)

        next_button = QPushButton("Next")
        next_button.clicked.connect(self.save_and_continue)
        layout.addWidget(next_button)

        self.setLayout(layout)

        # Load defaults into UI
        self.populate_fields()

    def populate_fields(self):
        self.cam_x.setValue(self.state.cam_res_x)
        self.cam_y.setValue(self.state.cam_res_y)
        self.cam_px.setValue(self.state.cam_pixel_size)

        self.slm_x.setValue(self.state.slm_res_x)
        self.slm_y.setValue(self.state.slm_res_y)
        self.slm_px.setValue(self.state.slm_pixel_size)

    def save_and_continue(self):
        self.update_state()
        self.go_next()

    def save_as_default(self):
        self.update_state()
        self.state.save_defaults()
        print("Defaults Saved")

    def update_state(self):
        self.state.cam_res_x = self.cam_x.value()
        self.state.cam_res_y = self.cam_y.value()
        self.state.cam_pixel_size = self.cam_px.value()

        self.state.slm_res_x = self.slm_x.value()
        self.state.slm_res_y = self.slm_y.value()
        self.state.slm_pixel_size = self.slm_px.value()