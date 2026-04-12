import os
import subprocess
import tempfile
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
import webbrowser

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "images"
SUPPORTED_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif")


SENSOR_DB = {
    "Rowek T": [
        {"name": "BMF00C4", "link": "https://www.balluff.com/pl-pl/products/BMF00C4"},
        {"name": "BMF00AR", "link": "https://www.balluff.com/pl-pl/products/BMF00AR"},
    ],
    "Rowek C": [
        {
            "name": "BMF00P0",
            "link": "https://www.balluff.com/en-us/products/BMF00P0?pm=BMF423&pf=F01502",
        },
        {"name": "Sensor C-2", "link": "https://twoj-link.pl/sensor-c-2"},
    ],
    "Rowek specjalny": [
        {"name": "Sensor S-1", "link": "https://twoj-link.pl/sensor-s-1"},
    ],
}


# Podaj nazwe pliku bez rozszerzenia albo pelna sciezke wzgledem katalogu programu.
GROOVE_IMAGES = {
    "Rowek T": "images/rowek_t.jpg",
    "Rowek C": "images/rowek_c.jpg",
    "Rowek specjalny": "images/rowek_trapezowy.jpg",
}


class SensorConfiguratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Konfigurator sensorow do silownika")
        self.geometry("1000x650")
        self.minsize(900, 600)

        self.selected_groove = tk.StringVar(value="")
        self.checkbox_vars = {}
        self.current_photo = None
        self._temp_image_path = None

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        main = ttk.Frame(self, padding=12)
        main.pack(fill="both", expand=True)

        title = ttk.Label(
            main,
            text="Konfigurator sensorow wedlug rowka silownika",
            font=("Segoe UI", 16, "bold"),
        )
        title.pack(anchor="w", pady=(0, 10))

        content = ttk.Frame(main)
        content.pack(fill="both", expand=True)

        left = ttk.Frame(content, padding=(0, 0, 12, 0))
        left.pack(side="left", fill="y")

        groove_box = ttk.LabelFrame(left, text="1. Wybierz typ rowka", padding=10)
        groove_box.pack(fill="x", pady=(0, 10))

        for groove_name in SENSOR_DB.keys():
            ttk.Radiobutton(
                groove_box,
                text=groove_name,
                value=groove_name,
                variable=self.selected_groove,
                command=self.on_groove_change,
            ).pack(anchor="w", pady=3)

        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(btn_frame, text="Pokaz sensory", command=self.show_sensors).pack(
            fill="x", pady=4
        )
        ttk.Button(btn_frame, text="Wyczysc wybor", command=self.clear_selection).pack(
            fill="x", pady=4
        )
        ttk.Button(btn_frame, text="Pokaz podsumowanie", command=self.show_summary).pack(
            fill="x", pady=4
        )

        right = ttk.Frame(content)
        right.pack(side="left", fill="both", expand=True)

        image_box = ttk.LabelFrame(right, text="2. Zdjecie / podglad rowka", padding=10)
        image_box.pack(fill="x", pady=(0, 10))

        self.image_label = ttk.Label(
            image_box,
            text=(
                "Tutaj bedzie wyswietlane zdjecie wybranego rowka.\n\n"
                "Program szuka plikow w folderze images (.png, .jpg, .jpeg, .gif)."
            ),
            anchor="center",
            justify="center",
        )
        self.image_label.pack(fill="x")

        sensor_box = ttk.LabelFrame(right, text="3. Dostepne sensory", padding=10)
        sensor_box.pack(fill="both", expand=True)

        canvas = tk.Canvas(sensor_box, highlightthickness=0)
        scrollbar = ttk.Scrollbar(sensor_box, orient="vertical", command=canvas.yview)
        self.sensor_list_frame = ttk.Frame(canvas)

        self.sensor_list_frame.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=self.sensor_list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.result_box = ttk.LabelFrame(right, text="4. Podsumowanie", padding=10)
        self.result_box.pack(fill="x", pady=(10, 0))

        self.result_label = ttk.Label(
            self.result_box,
            text="Wybierz typ rowka i zaznacz sensory checkboxem.",
            justify="left",
        )
        self.result_label.pack(anchor="w")

    def on_groove_change(self):
        self.load_image()
        self.show_sensors()

    def load_image(self):
        groove = self.selected_groove.get()
        image_key = GROOVE_IMAGES.get(groove, "")

        if not groove:
            self.image_label.config(text="Nie wybrano typu rowka.", image="")
            self.current_photo = None
            return

        if not image_key:
            self.image_label.config(
                text=f"Brak przypisanego zdjecia dla: {groove}",
                image="",
            )
            self.current_photo = None
            return

        path = self._resolve_image_path(image_key)
        if not path.exists():
            self.image_label.config(
                text=(
                    f"Nie znaleziono pliku zdjecia:\n{path}\n\n"
                    "Sprawdz folder images oraz wpis w GROOVE_IMAGES."
                ),
                image="",
            )
            self.current_photo = None
            return

        try:
            self.current_photo = self._create_photo(path)
            self.image_label.config(text="", image=self.current_photo)
        except Exception as exc:
            details = (
                "Dla JPG/JPEG program potrzebuje biblioteki Pillow "
                "(instalacja: pip install pillow)."
                if path.suffix.lower() in {".jpg", ".jpeg"}
                else "Plik istnieje, ale nie udalo sie go wyswietlic."
            )
            self.image_label.config(
                text=f"{details}\n\nPlik: {path}\n\nSzczegoly: {exc}",
                image="",
            )
            self.current_photo = None

    def _resolve_image_path(self, image_key):
        raw_path = Path(image_key)
        if not raw_path.is_absolute():
            if raw_path.parts and raw_path.parts[0].lower() == "images":
                raw_path = BASE_DIR / raw_path
            else:
                raw_path = IMAGES_DIR / raw_path

        if raw_path.suffix:
            return raw_path

        for extension in SUPPORTED_IMAGE_EXTENSIONS:
            candidate = raw_path.with_suffix(extension)
            if candidate.exists():
                return candidate

        return raw_path

    def _create_photo(self, path):
        self._cleanup_temp_image()

        if path.suffix.lower() in {".jpg", ".jpeg"}:
            if Image is not None and ImageTk is not None:
                image = Image.open(path)
                return ImageTk.PhotoImage(image)

            converted_path = self._convert_jpg_to_png(path)
            self._temp_image_path = converted_path
            return tk.PhotoImage(file=str(converted_path))

        return tk.PhotoImage(file=str(path))

    @staticmethod
    def _convert_jpg_to_png(path):
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        temp_file.close()

        command = [
            "powershell",
            "-NoProfile",
            "-Command",
            (
                "Add-Type -AssemblyName System.Drawing; "
                "$inputPath = [System.IO.Path]::GetFullPath($args[0]); "
                "$outputPath = [System.IO.Path]::GetFullPath($args[1]); "
                "$image = [System.Drawing.Image]::FromFile($inputPath); "
                "$image.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png); "
                "$image.Dispose()"
            ),
            str(path),
            temp_file.name,
        ]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except Exception as exc:
            try:
                os.unlink(temp_file.name)
            except OSError:
                pass
            raise RuntimeError("Nie udalo sie przekonwertowac JPG do PNG.") from exc

        return Path(temp_file.name)

    def _cleanup_temp_image(self):
        if not self._temp_image_path:
            return

        try:
            os.unlink(self._temp_image_path)
        except OSError:
            pass
        finally:
            self._temp_image_path = None

    def _on_close(self):
        self._cleanup_temp_image()
        self.destroy()

    def show_sensors(self):
        for widget in self.sensor_list_frame.winfo_children():
            widget.destroy()

        self.checkbox_vars.clear()

        groove = self.selected_groove.get()
        if not groove:
            ttk.Label(
                self.sensor_list_frame,
                text="Najpierw wybierz typ rowka po lewej stronie.",
            ).pack(anchor="w")
            return

        sensors = SENSOR_DB.get(groove, [])
        if not sensors:
            ttk.Label(
                self.sensor_list_frame,
                text=f"Brak sensorow przypisanych do typu: {groove}",
            ).pack(anchor="w")
            return

        ttk.Label(
            self.sensor_list_frame,
            text=f"Typ rowka: {groove}",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        for idx, sensor in enumerate(sensors):
            row = ttk.Frame(self.sensor_list_frame)
            row.pack(fill="x", pady=4)

            var = tk.BooleanVar(value=False)
            self.checkbox_vars[idx] = (var, sensor)
            sensor_name = self._get_sensor_name(sensor)
            sensor_link = self._get_sensor_link(sensor)

            ttk.Checkbutton(
                row,
                text=sensor_name,
                variable=var,
                command=self.update_summary_text,
            ).pack(side="left", anchor="w")

            ttk.Button(
                row,
                text="Otworz link",
                command=lambda url=sensor_link: self.open_link(url),
            ).pack(side="right")

    def update_summary_text(self):
        groove = self.selected_groove.get()
        selected = []

        for var, sensor in self.checkbox_vars.values():
            if var.get():
                selected.append(self._get_sensor_name(sensor))

        if not groove:
            text = "Nie wybrano typu rowka."
        elif not selected:
            text = f"Wybrany rowek: {groove}\nNie zaznaczono jeszcze zadnego sensora."
        else:
            text = f"Wybrany rowek: {groove}\nZaznaczone sensory:\n- " + "\n- ".join(selected)

        self.result_label.config(text=text)

    def show_summary(self):
        groove = self.selected_groove.get()
        if not groove:
            messagebox.showwarning("Brak wyboru", "Najpierw wybierz typ rowka.")
            return

        selected = []
        for var, sensor in self.checkbox_vars.values():
            if var.get():
                selected.append(
                    f"{self._get_sensor_name(sensor)}\n{self._get_sensor_link(sensor)}"
                )

        if not selected:
            messagebox.showinfo(
                "Podsumowanie",
                f"Wybrany rowek: {groove}\n\nNie zaznaczono zadnego sensora.",
            )
            return

        summary = f"Wybrany rowek: {groove}\n\nDopasowane sensory:\n\n- " + "\n\n- ".join(selected)
        messagebox.showinfo("Podsumowanie", summary)
        self.update_summary_text()

    def clear_selection(self):
        self.selected_groove.set("")
        self.current_photo = None
        self._cleanup_temp_image()
        self.image_label.config(
            text=(
                "Tutaj bedzie wyswietlane zdjecie wybranego rowka.\n\n"
                "Program szuka plikow w folderze images (.png, .jpg, .jpeg, .gif)."
            ),
            image="",
        )

        for widget in self.sensor_list_frame.winfo_children():
            widget.destroy()

        self.checkbox_vars.clear()
        self.result_label.config(text="Wybierz typ rowka i zaznacz sensory checkboxem.")

    @staticmethod
    def open_link(url):
        if not url:
            messagebox.showwarning("Brak linku", "Ten sensor nie ma przypisanego linku.")
            return

        try:
            if webbrowser.open_new_tab(url):
                return
        except Exception:
            pass

        try:
            os.startfile(url)
            return
        except OSError:
            messagebox.showerror(
                "Blad otwierania linku",
                f"Nie udalo sie otworzyc linku:\n{url}",
            )

    @staticmethod
    def _get_sensor_name(sensor):
        if isinstance(sensor, str):
            return sensor

        if not isinstance(sensor, dict):
            return str(sensor)

        for key in ("name", "nazwa", "sensor", "sensor_name", "title", "label"):
            value = sensor.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        for value in sensor.values():
            if isinstance(value, str) and value.strip():
                return value.strip()

        return "Sensor bez nazwy"

    @staticmethod
    def _get_sensor_link(sensor):
        if isinstance(sensor, dict):
            for key in ("link", "url", "href"):
                value = sensor.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()

        return ""


if __name__ == "__main__":
    app = SensorConfiguratorApp()
    app.mainloop()
