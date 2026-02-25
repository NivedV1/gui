import json
import os


class AppState:
    def __init__(self):
        # Camera parameters
        self.cam_res_x = 1024
        self.cam_res_y = 1024
        self.cam_pixel_size = 1.0

        # SLM parameters
        self.slm_res_x = 1024
        self.slm_res_y = 1024
        self.slm_pixel_size = 8.0

        # Clicked points from grid (centered coordinates)
        self.clicked_points = []

        # Alias used by GS page (same list)
        self.trap_positions = self.clicked_points

        self.config_path = "config.json"

        self.load_defaults()

    def to_dict(self):
        return {
            "cam_res_x": self.cam_res_x,
            "cam_res_y": self.cam_res_y,
            "cam_pixel_size": self.cam_pixel_size,
            "slm_res_x": self.slm_res_x,
            "slm_res_y": self.slm_res_y,
            "slm_pixel_size": self.slm_pixel_size,
        }

    def save_defaults(self):
        with open(self.config_path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def load_defaults(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                data = json.load(f)

            self.cam_res_x = data.get("cam_res_x", self.cam_res_x)
            self.cam_res_y = data.get("cam_res_y", self.cam_res_y)
            self.cam_pixel_size = data.get("cam_pixel_size", self.cam_pixel_size)

            self.slm_res_x = data.get("slm_res_x", self.slm_res_x)
            self.slm_res_y = data.get("slm_res_y", self.slm_res_y)
            self.slm_pixel_size = data.get("slm_pixel_size", self.slm_pixel_size)