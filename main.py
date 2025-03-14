# =================
# Imports
# =================

import customtkinter as ctki
from utils import DownloadAdaptive, DownloadProgressive, CombineAV, GetStreams
from dotenv import load_dotenv
import os
from PIL import Image, ImageTk

# =================
# Globals
# =================
load_dotenv()
PROGRESSIVE = False

# .env
DEFAULT_PATH = os.getenv("DEFAULT_PATH")
DOWNLOAD_URL = os.getenv("DOWNLOAD_URL")


# =================
# Classes
# =================
class BaseFrame(ctki.CTkScrollableFrame):
    def __init__(self, master, width=600, corner_radius=10):
        super().__init__(master, width=width, corner_radius=corner_radius)

        self.grid_columnconfigure((0, 1, 2), weight=1)

        # URL
        self.url_frame = URLFrame(self)
        self.url_frame.grid(row=1, column=0, padx=10, pady=10)

        # Download
        self.download_button = ctki.CTkButton(
            self, text="Download", command=self.download_button_click)
        self.download_button.grid(row=2, column=0, padx=20, pady=20)

    def download_button_click(self):
        print("download pressed")


class TitleFrame(ctki.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.title = ctki.CTkLabel(
            self, text="PYTDL: simple youtube downloader", font=("Roboto-Regular", 24))
        self.title.grid(row=0, column=0, padx=0, pady=0)


class URLFrame(ctki.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # Title
        self.title = ctki.CTkLabel(self, text="Paste URL here:")
        self.title.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Textbox
        self.url_textbox = ctki.CTkTextbox(
            self, height=20, width=600, corner_radius=10)
        self.url_textbox.grid(row=1, column=0, padx=10,
                              pady=(5, 10), sticky="ew")

        self.audio_only_var = ctki.StringVar(value="off")
        self.audio_only = ctki.CTkCheckBox(
            self,
            text="Audio Only",
            command=self.audio_only_event,
            variable=self.audio_only_var,
            onvalue="on",
            offvalue="off"
        )
        self.audio_only.grid(row=2, column=0, padx=20,
                             pady=(0, 10), sticky="w")

        self.get_streams = ctki.CTkButton(
            self,
            text="Get Options",
            command=self.get_streams_event,
        )
        self.get_streams.grid(
            row=3,
            column=0,
            padx=5,
            pady=5,
            sticky="ew"
        )

        self.thumb_placeholder = Image.new("RGB", (100, 100), color="black")
        self.thumb_placeholder_img = ImageTk.PhotoImage(self.thumb_placeholder)
        self.thumb_label = ctki.CTkLabel(
            self, image=self.thumb_placeholder_img, text="")
        self.thumb_label.grid(
            row=4,
            column=0,
            padx=10,
            pady=10,
            sticky="ew"
        )

    def audio_only_event(self):
        print("Checkbox toggled: ", self.audio_only_var.get())

    def get_streams_event(self):
        print("Get Streams pressed")
        url = self.url_textbox.get("0.0", "end").rstrip("\n")
        only_audio = self.audio_only_var.get() == "on"

        if url:
            print(url)
            data = GetStreams(url, only_audio)
            if data["thumbnail"]:
                thumbnail = ImageTk.PhotoImage(data["thumbnail"])
                self.thumb_label.configure(image=thumbnail)
        else:
            print("No URL")


class App(ctki.CTk):
    def __init__(self):
        super().__init__()

        # Window
        self.title("Pytdl")
        self.geometry("1280x720")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title
        self.title_frame = TitleFrame(self)
        self.title_frame.grid(row=0, column=0, padx=20, pady=20)

        # Base
        self.base_frame = BaseFrame(self)
        self.base_frame.grid(row=1, column=0, pady=20, sticky="ns")


def Main():
    """
    if PROGRESSIVE:
        v = DownloadProgressive(DOWNLOAD_URL, DEFAULT_PATH)
    else:
        v, a, t = DownloadAdaptive(DOWNLOAD_URL, DEFAULT_PATH)
        CombineAV(v, a, DEFAULT_PATH, t)
    """

    app = App()
    app.mainloop()


if __name__ == "__main__":
    Main()
