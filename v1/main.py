# main.py
"""
PySide6 GUI integrating a 50x50 clickable grid (left), a center image showing the
GS target intensity, and a right image showing the retrieved phase map (visualized).
Requires: PySide6, numpy
Place mainwindow.ui in the same folder as this script.
"""

import sys
from pathlib import Path
import os
import numpy as np
from PySide6 import QtWidgets, QtGui, QtCore, QtUiTools

BASE_DIR = Path(__file__).parent
UI_FILE = BASE_DIR / "mainwindow.ui"

if not UI_FILE.exists():
    raise FileNotFoundError(f"UI file not found at: {UI_FILE.resolve()}")

# ---------------- GridWidget ----------------
class GridWidget(QtWidgets.QWidget):
    coordinateClicked = QtCore.Signal(int, int)

    def __init__(self, rows=50, cols=50, parent=None):
        super().__init__(parent)
        self.rows = rows
        self.cols = cols
        self.setMouseTracking(True)
        self.bg_color = QtGui.QColor(250, 250, 250)
        self.line_color = QtGui.QColor(200, 200, 200)
        self.hover_cell = None

    def sizeHint(self):
        return QtCore.QSize(300, 300)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, False)
        painter.fillRect(self.rect(), self.bg_color)

        w = self.width()
        h = self.height()
        if self.cols <= 0 or self.rows <= 0:
            return

        cell_w = w / self.cols
        cell_h = h / self.rows

        pen = QtGui.QPen(self.line_color)
        pen.setWidth(1)
        painter.setPen(pen)

        if self.hover_cell is not None:
            r, c = self.hover_cell
            rect = QtCore.QRectF(c * cell_w, r * cell_h, cell_w, cell_h)
            painter.fillRect(rect, QtGui.QColor(180, 200, 255, 80))

        x = 0.0
        for _ in range(self.cols + 1):
            painter.drawLine(QtCore.QPointF(x, 0.0), QtCore.QPointF(x, h))
            x += cell_w

        y = 0.0
        for _ in range(self.rows + 1):
            painter.drawLine(QtCore.QPointF(0.0, y), QtCore.QPointF(w, y))
            y += cell_h

        painter.end()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() != QtCore.Qt.LeftButton:
            return
        r, c = self._pos_to_cell(event.pos())
        if 0 <= r < self.rows and 0 <= c < self.cols:
            self.coordinateClicked.emit(r, c)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        r, c = self._pos_to_cell(event.pos())
        if (r, c) != self.hover_cell:
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self.hover_cell = (r, c)
            else:
                self.hover_cell = None
            self.update()

    def leaveEvent(self, event):
        self.hover_cell = None
        self.update()

    def _pos_to_cell(self, pos: QtCore.QPoint):
        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return -1, -1
        cell_w = w / self.cols
        cell_h = h / self.rows
        col = int(pos.x() / cell_w)
        row = int(pos.y() / cell_h)
        return row, col


# ---------------- GS algorithm (adapted) ----------------
def run_gs_algorithm(N=400, n_iters=200, f0=5):
    """
    Runs the Gerchberg-Saxton loop as in the user's script.
    Returns:
      A_source: source amplitude (N x N, normalized)
      I_target: target intensity (N x N, normalized)
      phase_retrieved: retrieved phase (radians, range -pi..pi)
      I_result: final output intensity from retrieved phase (normalized)
    """
    x = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(x, x)

    # Source amplitude
    A_source = np.exp(-1 * ((X) ** 2 + Y ** 2) / 20.0)
    A_source = A_source / A_source.max()

    # Known phase to create a target intensity (phase5)
    phase5 = np.sin(5 * np.pi * f0 * X)
    U = A_source * np.exp(1j * phase5)

    # Forward propagate to get target intensity
    U_f5 = np.fft.fftshift(np.fft.fft2(U))
    I_result1 = np.abs(U_f5) ** 2
    I_result1 = I_result1 / I_result1.max()
    I_target = I_result1
    A_target = np.sqrt(I_target)
    A_target = A_target / A_target.max()

    # Initialize U with some phase (random-ish)
    phase_init = (np.sin(5 * np.pi * X)) * (np.sin(5 * np.pi * Y))
    U = A_source * np.exp(1j * phase_init)

    corr_history = []

    for i in range(n_iters):
        # Forward propagation
        U_f = np.fft.fftshift(np.fft.fft2(U))

        # Enforce target amplitude (GS)
        U_f = A_target * np.exp(1j * np.angle(U_f))

        # Backward propagation
        U = np.fft.ifft2(np.fft.ifftshift(U_f))

        # Enforce source amplitude
        U = A_source * np.exp(1j * np.angle(U))

        # Correlation (monitor)
        U_test_f = np.fft.fftshift(np.fft.fft2(U))
        I_test = np.abs(U_test_f) ** 2
        I_test = I_test / I_test.max()

        corr = np.corrcoef(I_test.ravel(), (I_target / I_target.max()).ravel())[0, 1]
        corr_history.append(corr)

    # Retrieved phase
    phase_retrieved = np.angle(U)

    # Final intensity from retrieved phase (no constraints)
    U_test = A_source * np.exp(1j * phase_retrieved)
    U_test_f = np.fft.fftshift(np.fft.fft2(U_test))
    I_result = np.abs(U_test_f) ** 2
    I_result = I_result / I_result.max()

    return A_source, I_target, phase_retrieved, I_result, corr_history


# ---------------- Helpers: convert numpy arrays to QPixmap ----------------
def array_to_qpixmap_gray(arr):
    """
    Convert a 2D numpy array (float, 0..1 or arbitrary) to a QPixmap (grayscale).
    Scales to 0..255 and creates QImage then QPixmap.
    """
    if arr is None:
        return None
    a = np.array(arr, dtype=np.float64)
    # normalize to 0..1
    a_min = a.min()
    a_max = a.max()
    if a_max - a_min > 0:
        a = (a - a_min) / (a_max - a_min)
    else:
        a = np.zeros_like(a)
    a8 = (255.0 * a).astype(np.uint8)
    h, w = a8.shape
    # QImage expects bytes in row-major order
    qimg = QtGui.QImage(a8.data, w, h, w, QtGui.QImage.Format_Grayscale8)
    # make a deep copy because the numpy buffer may go out of scope
    qimg = qimg.copy()
    return QtGui.QPixmap.fromImage(qimg)


def phase_to_qpixmap(phase_array):
    """
    Convert phase (radians) to grayscale image by mapping phase to 0..1.
    phase in [-pi, pi] -> (phase + pi) / (2*pi)
    """
    if phase_array is None:
        return None
    mapped = (phase_array + np.pi) / (2 * np.pi)
    return array_to_qpixmap_gray(mapped)


# ---------------- UI Controller ----------------
class UIController(QtCore.QObject):
    def __init__(self, ui_path: Path):
        super().__init__()
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(str(ui_path))
        if not ui_file.open(QtCore.QFile.ReadOnly):
            raise RuntimeError(f"Failed to open UI file: {ui_path}")
        try:
            self.loaded = loader.load(ui_file)
        finally:
            ui_file.close()

        if self.loaded is None:
            raise RuntimeError("QUiLoader failed to load the UI file.")

        if isinstance(self.loaded, QtWidgets.QMainWindow):
            self.window = self.loaded
            self.ui = self.loaded
        else:
            self.window = QtWidgets.QMainWindow()
            self.window.setCentralWidget(self.loaded)
            self.ui = self.loaded

        self._find_widgets()
        self._setup_grid()
        # Run GS algorithm once at startup (can be triggered later if desired)
        self._run_gs_and_prepare_pixmaps()
        self._setup_images()
        self._setup_start_progress()
        self.window.installEventFilter(self)

    def _find_widgets(self):
        self.grid_placeholder = self.ui.findChild(QtWidgets.QWidget, "gridPlaceholder")
        self.coord_left_label = self.ui.findChild(QtWidgets.QLabel, "coordLeft")
        self.title_left = self.ui.findChild(QtWidgets.QLabel, "titleLeft")

        self.center_label = self.ui.findChild(QtWidgets.QLabel, "label_12")
        self.right_label = self.ui.findChild(QtWidgets.QLabel, "label_11")
        self.switch_button = self.ui.findChild(QtWidgets.QPushButton, "switchButton")
        self.title_center = self.ui.findChild(QtWidgets.QLabel, "titleCenter")
        self.title_right = self.ui.findChild(QtWidgets.QLabel, "titleRight")

        self.start_button = self.ui.findChild(QtWidgets.QPushButton, "startButton")
        self.progress_bar = self.ui.findChild(QtWidgets.QProgressBar, "progressBar")

    def _setup_grid(self):
        self.grid_widget = GridWidget(rows=50, cols=50, parent=self.window)
        if self.grid_placeholder:
            parent = self.grid_placeholder.parentWidget()
            if parent and parent.layout():
                try:
                    parent.layout().replaceWidget(self.grid_placeholder, self.grid_widget)
                    self.grid_placeholder.hide()
                    self.grid_widget.show()
                except Exception:
                    parent.layout().addWidget(self.grid_widget)
                    self.grid_placeholder.hide()
                    self.grid_widget.show()
            else:
                self.grid_widget.setParent(self.window)
                self.grid_widget.setGeometry(self.grid_placeholder.geometry() if self.grid_placeholder else QtCore.QRect(0, 0, 300, 300))
                self.grid_widget.show()
                if self.grid_placeholder:
                    self.grid_placeholder.hide()
        else:
            if isinstance(self.ui.layout(), QtWidgets.QLayout):
                self.ui.layout().addWidget(self.grid_widget)

        self.grid_widget.coordinateClicked.connect(self.on_grid_clicked)

    def _run_gs_and_prepare_pixmaps(self):
        """
        Run the GS algorithm and prepare QPixmaps for center (target intensity)
        and right (retrieved phase). Also keep final GS output intensity if needed.
        """
        # Parameters can be adjusted or exposed in UI
        N = 400
        n_iters = 200
        f0 = 5

        A_source, I_target, phase_retrieved, I_result, corr_history = run_gs_algorithm(N=N, n_iters=n_iters, f0=f0)

        # Save arrays for potential later use
        self._A_source = A_source
        self._I_target = I_target
        self._phase_retrieved = phase_retrieved
        self._I_result = I_result
        self._corr_history = corr_history

        # Convert to QPixmaps (grayscale)
        self._center_pixmap_full = array_to_qpixmap_gray(I_target)          # center: target intensity
        self._right_pixmap_full = phase_to_qpixmap(phase_retrieved)        # right: retrieved phase visualization
        # Optionally store final output intensity pixmap if needed
        self._final_output_pixmap_full = array_to_qpixmap_gray(I_result)

    def _setup_images(self):
        # Connect switch button to cycle center image through center pixmaps.
        # In this integration, center cycles through a list of target intensities if desired.
        # For now we have a single target intensity; clicking will re-run GS and update center.
        if self.switch_button:
            self.switch_button.clicked.connect(self.on_switch)

        # initial display
        self.update_all_images()

    def _setup_start_progress(self):
        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._on_timer_tick)
        if self.start_button:
            self.start_button.clicked.connect(self.on_start_clicked)
        if self.progress_bar:
            self.progress_bar.setValue(0)

    # ---------- Actions ----------
    def on_start_clicked(self):
        if not self.progress_bar or not self.start_button:
            return
        self.start_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self._timer.start()

    def _on_timer_tick(self):
        if not self.progress_bar:
            return
        val = self.progress_bar.value() + 2
        if val >= 100:
            val = 100
            self.progress_bar.setValue(val)
            self._timer.stop()
            if self.start_button:
                self.start_button.setEnabled(True)
        else:
            self.progress_bar.setValue(val)

    def on_grid_clicked(self, row: int, col: int):
        if self.coord_left_label:
            self.coord_left_label.setText(f"Clicked: {row} , {col}")

    def on_switch(self):
        """
        In this integration the 'Switch Image' button will re-run the GS algorithm
        (or advance through multiple prepared center images if you prepare more).
        Here we re-run GS to demonstrate updating the center image while keeping
        the right image as the retrieved phase from the latest run.
        """
        # Re-run GS (this is potentially heavy; consider running in a worker thread for responsiveness)
        self._run_gs_and_prepare_pixmaps()
        self.update_all_images()

    def update_all_images(self):
        """
        Set center and right label pixmaps. Scale pixmaps to label size to avoid distortion.
        """
        # center
        if hasattr(self, "_center_pixmap_full") and self._center_pixmap_full is not None and self.center_label is not None:
            pm = self._center_pixmap_full
            scaled = pm.scaled(self.center_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.center_label.setPixmap(scaled)
            self.center_label.setAlignment(QtCore.Qt.AlignCenter)
            self.center_label.setStyleSheet("")
        else:
            if self.center_label:
                self.center_label.clear()
                self.center_label.setText("No image")
                self.center_label.setAlignment(QtCore.Qt.AlignCenter)

        # right
        if hasattr(self, "_right_pixmap_full") and self._right_pixmap_full is not None and self.right_label is not None:
            pm = self._right_pixmap_full
            scaled = pm.scaled(self.right_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.right_label.setPixmap(scaled)
            self.right_label.setAlignment(QtCore.Qt.AlignCenter)
            self.right_label.setStyleSheet("")
        else:
            if self.right_label:
                self.right_label.clear()
                self.right_label.setText("No image")
                self.right_label.setAlignment(QtCore.Qt.AlignCenter)

        # update titles
        if self.title_center:
            self.title_center.setText("Center: Target Intensity")
        if self.title_right:
            self.title_right.setText("Right: Retrieved Phase")

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Resize:
            # rescale center and right images on resize
            if hasattr(self, "_center_pixmap_full") and self._center_pixmap_full is not None and self.center_label is not None:
                pm = self._center_pixmap_full
                scaled = pm.scaled(self.center_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                self.center_label.setPixmap(scaled)
            if hasattr(self, "_right_pixmap_full") and self._right_pixmap_full is not None and self.right_label is not None:
                pm = self._right_pixmap_full
                scaled = pm.scaled(self.right_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                self.right_label.setPixmap(scaled)
        return False

    def show(self):
        self.window.show()


# ---------------- main ----------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName("MyCompany")
    app.setApplicationName("GSImageApp")
    controller = UIController(UI_FILE)
    controller.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
