from app import App

# FIX: error when making a second stream request
# TODO: add a field to give download path


def Main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    Main()
