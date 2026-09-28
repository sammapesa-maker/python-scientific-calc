"""Main application window — assembles display and button panel."""

import tkinter as tk
from controller import CalculatorController
from .display import Display
from .button_panel import ButtonPanel


class CalculatorApp:
    """Top-level calculator GUI."""

    def __init__(self, root: tk.Tk, controller: CalculatorController):
        self._root = root
        self._controller = controller

        self._configure_window()
        self._build_widgets()
        self._register_callbacks()
        self._bind_keyboard()

        # Set initial mode display
        self._button_panel.update_mode_label(controller.angle_mode.value)

    def _configure_window(self):
        self._root.title("Scientific Calculator")
        self._root.configure(bg="#1e1e2e")
        self._root.resizable(True, True)
        self._root.minsize(400, 600)
        # Start at a comfortable size
        self._root.geometry("420x680")

    def _build_widgets(self):
        # Display at the top
        self._display = Display(self._root)
        self._display.pack(fill="x", padx=5, pady=(5, 0))

        # Button panel fills the rest
        self._button_panel = ButtonPanel(
            self._root,
            on_input=self._controller.on_input,
            on_evaluate=self._controller.on_evaluate,
            on_clear=self._controller.on_clear,
            on_backspace=self._controller.on_backspace,
            on_toggle_mode=self._controller.on_toggle_angle_mode,
            on_negate=self._controller.on_negate,
        )
        self._button_panel.pack(fill="both", expand=True, padx=5, pady=5)

    def _register_callbacks(self):
        """Tell the controller how to update the GUI."""
        self._controller.set_display_callback(self._display.update_display)
        self._controller.set_mode_callback(self._button_panel.update_mode_label)

    def _bind_keyboard(self):
        """Allow typing expressions with the keyboard."""
        self._root.bind('<Key>', self._on_key)
        self._root.bind('<Return>', lambda e: self._controller.on_evaluate())
        self._root.bind('<KP_Enter>', lambda e: self._controller.on_evaluate())
        self._root.bind('<BackSpace>', lambda e: self._controller.on_backspace())
        self._root.bind('<Escape>', lambda e: self._controller.on_clear())

    def _on_key(self, event):
        """Route keyboard characters to the controller."""
        char = event.char
        # Allow digits, operators, parens, dot
        allowed = set('0123456789+-*/().%^')
        if char in allowed:
            self._controller.on_input(char)