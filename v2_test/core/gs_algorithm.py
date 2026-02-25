import numpy as np


def gaussian_beam(nx, ny, sigma=0.45):
    """
    Gaussian beam amplitude (laser TEM00 mode)
    """
    x = np.linspace(-1, 1, nx)
    y = np.linspace(-1, 1, ny)
    X, Y = np.meshgrid(x, y)

    beam = np.exp(-(X**2 + Y**2) / (2 * sigma**2))
    return beam / beam.max()


def traps_to_target(trap_positions, nx, ny):
    """
    Create delta-function target intensity
    at selected trap positions.
    """
    target = np.zeros((ny, nx))

    cx = nx // 2
    cy = ny // 2

    for x, y in trap_positions:
        px = int(cx + x)
        py = int(cy - y)

        if 0 <= px < nx and 0 <= py < ny:
            target[py, px] = 1

    return target


# ✅ NEW: Binary phase grating initialization
def binary_grating_phase(nx, ny, period=16):
    """
    Create binary π-phase grating.

    period controls stripe width.
    Smaller period → stronger diffraction.
    """

    phase = np.zeros((ny, nx))

    for x in range(nx):
        if (x // period) % 2 == 1:
            phase[:, x] = np.pi

    return np.exp(1j * phase)


def gerchberg_saxton(source_amp, target_amp, iterations=500):
    """
    Gerchberg Saxton algorithm.

    Returns
    intensity  → focal plane traps
    phase_map  → SLM hologram phase
    """

    ny, nx = source_amp.shape

    # 🔹 Binary grating phase initialization
    phase_mask = binary_grating_phase(nx, ny, period=16)

    field = source_amp * phase_mask

    for _ in range(iterations):
        # forward propagation
        target_field = np.fft.fftshift(np.fft.fft2(field))

        # enforce target amplitude
        target_field = target_amp * np.exp(1j * np.angle(target_field))

        # back propagation
        field = np.fft.ifft2(np.fft.ifftshift(target_field))

        # enforce Gaussian amplitude
        field = source_amp * np.exp(1j * np.angle(field))

    final_field = np.fft.fftshift(np.fft.fft2(field))

    intensity = np.abs(final_field) ** 2
    intensity /= intensity.max()

    # phase at SLM plane
    phase_map = np.angle(field)

    return intensity, phase_map