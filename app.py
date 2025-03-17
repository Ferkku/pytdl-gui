# =================
# Imports
# =================
import customtkinter as ctki
import frames


# =================
# Classes
# =================
class App(ctki.CTk):
    def __init__(self):
        super().__init__()

        # Window
        self.title("Pytdl")
        self.geometry("1280x720")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title
        self.title_frame = frames.TitleFrame(self)
        self.title_frame.grid(row=0, column=0, padx=20, pady=20)

        # Base
        self.base_frame = frames.BaseFrame(self)
        self.base_frame.grid(row=1, column=0, pady=20, sticky="ns")
