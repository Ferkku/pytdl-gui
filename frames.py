# =================
# Imports
# =================
import customtkinter as ctki
from utils import Download, GetStreams
from PIL import Image, ImageTk
import tkinter
import os
import logging
import threading
import platform


# =================
# Globals
# =================

logging.basicConfig(level=logging.ERROR)

# =================
# Classes
# =================


class TitleFrame(ctki.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.title = ctki.CTkLabel(
            self, text="PYTDL: simple youtube downloader", font=("Roboto-Regular", 24))
        self.title.grid(row=0, column=0, padx=0, pady=0)


class BaseFrame(ctki.CTkScrollableFrame):
    def __init__(self, master, width=600, corner_radius=10):
        super().__init__(master, width=width, corner_radius=corner_radius)

        self.grid_columnconfigure(0, weight=1)

        if platform.system() != "Windows":
            self.mouse_wheel_event(master)

        self.only_audio_check = False

        self.streams = []
        self.stream_opt_radio = tkinter.IntVar(value=-1)
        self.video_title = ""

        self.download_path = os.getcwd()

        # URL
        self.url_frame = URLFrame(self)
        self.url_frame.grid(row=0, column=0, padx=10, pady=10)

        # STREAM OPTIONS
        self.stream_opts_frame = StreamOptionsFrame(self)
        self.stream_opts_frame.grid(row=1, column=0, padx=10, pady=10)

        # DOWNLOAD
        self.download_frame = DownloadFrame(self)
        self.download_frame.grid(row=2, column=0, padx=10, pady=10)

        # DOWNLOAD PATH
        self.download_path_frame = DownloadPathFrame(self)
        self.download_path_frame.grid(row=3, column=0, padx=10, pady=10)

    def mouse_wheel_event(self, master):
        def scroll(e):
            self._parent_canvas.yview_scroll(-1 * (e.delta // 120), "units")

        master.bind_all("<MouseWheel>", scroll)
        master.bind_all(
            "<Button-4>", lambda e: self._parent_canvas.yview_scroll(-1, "units"))
        master.bind_all(
            "<Button-5>", lambda e: self._parent_canvas.yview_scroll(1, "units"))


class DownloadPathFrame(ctki.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Title
        self.title = ctki.CTkLabel(self, text="Enter download path:")
        self.title.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Textbox
        self.path_textbox = ctki.CTkTextbox(
            self, height=20, width=500, corner_radius=10)
        self.path_textbox.grid(row=1, column=0, padx=10,
                               pady=(5, 5), sticky="ew")

        # Check path button
        self.check_path_button = ctki.CTkButton(
            self,
            text="Apply",
            command=self.check_download_path,
            width=30,
        )
        self.check_path_button.grid(
            row=1,
            column=1,
            padx=5,
            pady=5,
        )

        # Set path
        self.current_path = ctki.CTkLabel(
            self, text_color="white", text=f"Current: {master.download_path}")
        self.current_path.grid(row=2, column=0, padx=10, pady=0, sticky="w")

    def check_download_path(self):
        path = self.path_textbox.get("0.0", "end").rstrip("\n")

        if path == "":
            self.master.download_path = os.getcwd()
            self.current_path.configure(
                text_color="white", text=f"Current: {self.master.download_path}")
        elif os.path.exists(path):
            self.master.download_path = path
            self.current_path.configure(
                text_color="white", text=f"Current: {self.master.download_path}")
        else:
            self.master.download_path = ""
            self.current_path.configure(text_color="red", text="INVALID PATH")


class StreamOptionsFrame(ctki.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        # Thumbnail
        self.thumb_label = ctki.CTkLabel(self, text="")
        self.thumb_label.grid(
            row=0,
            column=0,
            padx=10,
            pady=(10, 0),
            sticky="ew"
        )

        # Video title
        self.video_title = ctki.CTkLabel(
            self, text=self.master.video_title, font=("Roboto-Regular", 16))
        self.video_title.grid(
            row=1,
            column=0,
            padx=10,
            pady=(0, 20),
            sticky="w",
        )

        self.radio_buttons = []

    def update_streams(self, data):
        for b in self.radio_buttons:
            b.destroy()
        self.radio_buttons.clear()

        if data:
            thumbnail = ImageTk.PhotoImage(data["thumbnail"])
            self.thumb_label.configure(image=thumbnail)
            self.master.video_title = data["title"]
            self.video_title.configure(text=self.master.video_title)
            self.master.streams = data["streams"].filter(
                only_audio=self.master.only_audio_check)

            row_index = 2

            for stream in self.master.streams:
                if stream.type == "audio":
                    but = ctki.CTkRadioButton(
                        self,
                        text=f"<{stream.mime_type}> <{stream.abr}>",
                        variable=self.master.stream_opt_radio,
                        value=stream.itag,
                        command=self.radio_selected,
                    )
                else:
                    but = ctki.CTkRadioButton(
                        self,
                        text=f"<{stream.mime_type}> <{stream.resolution}> <{stream.fps}fps>",
                        variable=self.master.stream_opt_radio,
                        value=stream.itag,
                        command=self.radio_selected,
                    )
                but.grid(
                    row=row_index, column=0, padx=20, pady=5, sticky="w")

                row_index += 1
                self.radio_buttons.append(but)

    def radio_selected(self):
        if self.master.stream_opt_radio.get() != 1:
            self.master.download_frame.download_button.configure(
                text="Download",
                state="normal",
            )


class DownloadFrame(ctki.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # Download
        self.download_button = ctki.CTkButton(
            self,
            text="Select Option",
            command=self.download_button_click,
            state="disabled",
        )
        self.download_button.grid(row=0, column=0, padx=20, pady=20)

    def download_button_click(self):
        if os.path.exists(self.master.download_path):
            opt = self.master.stream_opt_radio.get()
            if opt != -1:
                itag = self.master.stream_opt_radio.get()
                self.download_button.configure(
                    text="Downloading...", state="disabled")
                download_thread = threading.Thread(
                    target=Download,
                    args=(
                        itag,
                        self.master.streams,
                        self.master.download_path + "/",
                        self.master.video_title
                    ),
                    daemon=True
                )
                download_thread.start()
                self.check_download_thread(download_thread)
                self.master.stream_opt_radio.set(-1)

    def check_download_thread(self, t):
        if t.is_alive():
            self.after(100, lambda: self.check_download_thread(t))
        else:
            self.download_button.configure(
                text="Select Option", state="disabled")


class URLFrame(ctki.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_rowconfigure((1, 3), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title
        self.title = ctki.CTkLabel(self, text="Paste URL here:")
        self.title.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Textbox
        self.url_textbox = ctki.CTkTextbox(
            self, height=20, width=500, corner_radius=10)
        self.url_textbox.grid(row=1, column=0, padx=10,
                              pady=(5, 10), sticky="ew")

        # Audio only checkbox
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

        # Get stream button
        self.get_streams = ctki.CTkButton(
            self,
            text="Get Options",
            command=self.get_streams_event,
            width=200,
        )
        self.get_streams.grid(
            row=3,
            column=0,
            padx=5,
            pady=5,
        )

    def audio_only_event(self):
        logging.debug("Checkbox toggled: ", self.audio_only_var.get())
        if self.audio_only_var.get() == "on":
            self.master.only_audio_check = True
        else:
            self.master.only_audio_check = False

    def get_streams_event(self):
        logging.debug("Get Streams pressed")
        url = self.url_textbox.get("0.0", "end").rstrip("\n")

        if url:
            logging.debug(url)
            data = GetStreams(url)
            self.master.stream_opts_frame.update_streams(data)
        else:
            logging.debug("No URL")
