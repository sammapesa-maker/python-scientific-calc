"""Entry point for the scientific calculator application."""

import tkinter as tk
from controller import CalculatorController
from gui import CalculatorApp


def main():
    root = tk.Tk()
    controller = CalculatorController()
    app = CalculatorApp(root, controller)  # noqa: F841 — kept alive by mainloop
    root.mainloop()


if __name__ == "__main__":
    main()