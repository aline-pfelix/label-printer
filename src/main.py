import tkinter as tk

from ui import App


def main():
    root = tk.Tk()
    root.title("Label printer - Biodossel")

    app = App(root)

    root.mainloop()


if __name__ == "__main__":
    main()
