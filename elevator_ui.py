import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import logging
from typing import Optional
import os

# Import project functions
from main import (
    load_topography,
    resample_data,
    rotate_data,
    plot_topography,
    export_wavetable,
    TopDir,
)


class TextHandler(logging.Handler):
    """Logging handler that writes logs into a Tkinter Text widget."""
    def __init__(self, text_widget: ScrolledText):
        super().__init__()
        self.text_widget = text_widget
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, msg + "\n")
        self.text_widget.see(tk.END)
        self.text_widget.configure(state='disabled')


class ElevationUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Elevation Wavetable UI")
        self.geometry("940x600")

        self._data = None  # raw DEM as numpy array

        self._build_widgets()
        self._setup_logging()

    def _build_widgets(self):
        # Inputs frame
        frm_inputs = ttk.LabelFrame(self, text="Inputs")
        frm_inputs.pack(fill=tk.X, padx=8, pady=8)

        # Row 1: center and side_km
        ttk.Label(frm_inputs, text="Center (lat, lon)").grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        self.var_center = tk.StringVar(value="46.18870992001379, 8.843108172745026")
        ttk.Entry(frm_inputs, textvariable=self.var_center, width=40).grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)

        ttk.Label(frm_inputs, text="Size (km)").grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        self.var_side = tk.DoubleVar(value=10.0)
        ttk.Entry(frm_inputs, textvariable=self.var_side, width=10).grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)

        ttk.Label(frm_inputs, text="Top Direction").grid(row=0, column=2, sticky=tk.W, padx=4, pady=4)
        self.var_topdir = tk.StringVar(value="N")
        ttk.OptionMenu(frm_inputs, self.var_topdir, "N", "N", "E", "S", "W").grid(row=0, column=3, sticky=tk.W, padx=4, pady=4)

        # Row 2: frameSize, numFrames, rotation
        ttk.Label(frm_inputs, text="Frame Size").grid(row=0, column=4, sticky=tk.W, padx=4, pady=4)
        self.var_framesize = tk.IntVar(value=2048)
        ttk.Entry(frm_inputs, textvariable=self.var_framesize, width=10).grid(row=0, column=5, sticky=tk.W, padx=4, pady=4)

        ttk.Label(frm_inputs, text="Num Frames").grid(row=1, column=4, sticky=tk.W, padx=4, pady=4)
        self.var_numframes = tk.IntVar(value=256)
        ttk.Entry(frm_inputs, textvariable=self.var_numframes, width=10).grid(row=1, column=5, sticky=tk.W, padx=4, pady=4)

        # Row 3: Optional API key
        ttk.Label(frm_inputs, text="OpenTopography API Key (optional)").grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
        self.var_api_key = tk.StringVar(value=os.environ.get("OPENTOPOGRAPHY_API_KEY", ""))
        ttk.Entry(frm_inputs, textvariable=self.var_api_key, width=40).grid(row=2, column=1, columnspan=3, sticky=tk.W, padx=4, pady=4)


        # Buttons frame
        frm_buttons = ttk.Frame(self)
        frm_buttons.pack(fill=tk.X, padx=8, pady=4)

        ttk.Button(frm_buttons, text="Load Topography", command=self.on_load).pack(side=tk.LEFT, padx=4)
        ttk.Button(frm_buttons, text="Plot Topography", command=self.on_plot).pack(side=tk.LEFT, padx=4)
        ttk.Button(frm_buttons, text="Export Wavetable", command=self.on_export).pack(side=tk.LEFT, padx=4)

        # Log console
        frm_log = ttk.LabelFrame(self, text="Log")
        frm_log.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.txt_log = ScrolledText(frm_log, height=4, state='disabled')
        self.txt_log.pack(fill=tk.BOTH, expand=True)

        # Instructions
        frm_help = ttk.LabelFrame(self, text="Usage / Instructions")
        frm_help.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.txt_help = ScrolledText(frm_help, height=6)
        self.txt_help.pack(fill=tk.BOTH, expand=True)
        self._populate_help()
        self.txt_help.configure(state='disabled')

    def _setup_logging(self):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        # Avoid duplicate handlers when re-running
        for h in list(logger.handlers):
            logger.removeHandler(h)
        handler = TextHandler(self.txt_log)
        logger.addHandler(handler)
        self.logger = logger

    def _populate_help(self):
        msg = (
            "1) Enter center coordinate (lat, lon)\n"\
            "--> you can use google maps: right click on map and click on coordinates to copy in the correct format\n"
            "\n"
            "2) Enter size (km). (The length of the side of the square around the center.)\n"
            "\n"
            "3) Enter frame size. (Samples per frame)\n"
            "--> Serum and Vital Wavetable: 2028\n"
            "--> Ableton Wavetable and Bitwig: 1024\n"
            "\n"
            "4) Enter number of frames.\n"
            "--> highest resolution: 256. lower if you want smoother interpolation"

        )
        self.txt_help.insert(tk.END, msg)

    # Helpers
    def _parse_inputs(self) -> Optional[tuple]:
        try:
            center = self.var_center.get().strip()
            side_km = float(self.var_side.get())
            frame_size = int(self.var_framesize.get())
            num_frames = int(self.var_numframes.get())
            top_dir = TopDir[self.var_topdir.get()]
        except Exception as e:
            messagebox.showerror("Invalid input", str(e))
            return None
        return center, side_km, frame_size, num_frames, top_dir

    # Actions
    def on_load(self):
        parsed = self._parse_inputs()
        if not parsed:
            return
        center, side_km, _, _, _ = parsed
        try:
            # Set or unset API key
            api_key = self.var_api_key.get().strip()
            if api_key:
                os.environ["OPENTOPOGRAPHY_API_KEY"] = api_key
                self.logger.info("Using provided OpenTopography API key.")
            else:
                os.environ.pop("OPENTOPOGRAPHY_API_KEY", None)
                self.logger.info("No API key provided; using demo Key. (probably somewhat restricted idk)")

            self.logger.info(f"Loading DEM for center={center} side_km={side_km}")
            data = load_topography(center, side_km)
            self._data = data
            self.logger.info(f"Loaded DEM shape={getattr(data, 'shape', None)}")
        except Exception as e:
            self.logger.exception("Failed to load topography: %s", e)
            messagebox.showerror("Error", f"Failed to load topography:\n{e}")

    def _ensure_data(self) -> bool:
        if self._data is None:
            messagebox.showwarning("No data", "Please load topography first.")
            return False
        return True

    def _resample_and_rotate(self, frame_size: int, num_frames: int, top_dir: TopDir):
        # Resample then rotate according to UI
        res = resample_data(self._data, frame_size, num_frames)
        res = rotate_data(res, top_dir)
        return res

    def on_plot(self):
        parsed = self._parse_inputs()
        if not parsed or not self._ensure_data():
            return
        _, side_km, frame_size, num_frames, top_dir = parsed
        try:
            self.logger.info("Resampling and plotting topography ...")
            res = self._resample_and_rotate(frame_size, num_frames, top_dir)
            self.logger.info("close plot window to continue")
            plot_topography(res, side_km)
            self.logger.info("Plot done.")
        except Exception as e:
            self.logger.exception("Failed to plot: %s", e)
            messagebox.showerror("Error", f"Failed to plot:\n{e}")

    def on_export(self):
        parsed = self._parse_inputs()
        if not parsed or not self._ensure_data():
            return
        _, _, frame_size, num_frames, top_dir = parsed
        try:
            path = filedialog.asksaveasfilename(
                defaultextension=".wav",
                filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
                title="Save wavetable",
            )
            if not path:
                return
            self.logger.info("Resampling and exporting wavetable ...")
            res = self._resample_and_rotate(frame_size, num_frames, top_dir)
            _ = export_wavetable(res, filename=path)
            self.logger.info(f"Saved wavetable to {path}")
            messagebox.showinfo("Saved", f"Wavetable saved to:\n{path}")
        except Exception as e:
            self.logger.exception("Failed to export: %s", e)
            messagebox.showerror("Error", f"Failed to export:\n{e}")


if __name__ == "__main__":
    app = ElevationUI()
    app.mainloop()
