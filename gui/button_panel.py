"""Button grid construction and layout."""

import tkinter as tk
from typing import Callable


# ── Colour palette ──
COLORS = {
    "digit_bg":     "#313244",
    "digit_fg":     "#cdd6f4",
    "op_bg":        "#45475a",
    "op_fg":        "#fab387",
    "func_bg":      "#45475a",
    "func_fg":      "#89b4fa",
    "equals_bg":    "#a6e3a1",
    "equals_fg":    "#1e1e2e",
    "clear_bg":     "#f38ba8",
    "clear_fg":     "#1e1e2e",
    "mode_bg":      "#585b70",
    "mode_fg":      "#f5c2e7",
    "special_bg":   "#585b70",
    "special_fg":   "#cdd6f4",
}


class ButtonPanel(tk.Frame):
    """Grid of calculator buttons."""

    def __init__(
        self,
        parent,
        on_input: Callable[[str], None],
        on_evaluate: Callable[[], None],
        on_clear: Callable[[], None],
        on_backspace: Callable[[], None],
        on_toggle_mode: Callable[[], None],
        on_negate: Callable[[], None],
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        self.configure(bg="#1e1e2e")

        self._on_input = on_input
        self._on_evaluate = on_evaluate
        self._on_clear = on_clear
        self._on_backspace = on_backspace
        self._on_toggle_mode = on_toggle_mode
        self._on_negate = on_negate

        self._mode_button = None  # reference so we can update label

        self._build()

    def _build(self):
        """Lay out all buttons in a grid."""

        # Each entry: (text, col, row, col_span, type, action_override)
        # type: "digit", "op", "func", "equals", "clear", "mode", "special"

        buttons = [
            # ── Row 0: mode, backspace, clear ──
            ("DEG",  0, 0, 1, "mode",    self._on_toggle_mode),
            ("(",    1, 0, 1, "special",  None),
            (")",    2, 0, 1, "special",  None),
            ("⌫",   3, 0, 1, "clear",    self._on_backspace),
            ("C",    4, 0, 1, "clear",    self._on_clear),

            # ── Row 1: scientific ──
            ("sin",  0, 1, 1, "func", None),
            ("cos",  1, 1, 1, "func", None),
            ("tan",  2, 1, 1, "func", None),
            ("π",    3, 1, 1, "func", None),
            ("^",    4, 1, 1, "op",   None),

            # ── Row 2: scientific ──
            ("asin", 0, 2, 1, "func", None),
            ("acos", 1, 2, 1, "func", None),
            ("atan", 2, 2, 1, "func", None),
            ("e",    3, 2, 1, "func", None),
            ("x²",   4, 2, 1, "func", None),

            # ── Row 3: scientific ──
            ("sinh", 0, 3, 1, "func", None),
            ("cosh", 1, 3, 1, "func", None),
            ("tanh", 2, 3, 1, "func", None),
            ("√",    3, 3, 1, "func", None),
            ("x!",   4, 3, 1, "func", None),

            # ── Row 4: scientific + top digit row ──
            ("ln",   0, 4, 1, "func", None),
            ("log",  1, 4, 1, "func", None),
            ("eˣ",   2, 4, 1, "func", None),
            ("|x|",  3, 4, 1, "func", None),
            ("%",    4, 4, 1, "op",   None),

            # ── Row 5: digits ──
            ("7",    0, 5, 1, "digit", None),
            ("8",    1, 5, 1, "digit", None),
            ("9",    2, 5, 1, "digit", None),
            ("÷",    3, 5, 1, "op",    None),
            ("×",    4, 5, 1, "op",    None),

            # ── Row 6: digits ──
            ("4",    0, 6, 1, "digit", None),
            ("5",    1, 6, 1, "digit", None),
            ("6",    2, 6, 1, "digit", None),
            ("+",    3, 6, 1, "op",    None),
            ("-",    4, 6, 1, "op",    None),

            # ── Row 7: digits ──
            ("1",    0, 7, 1, "digit", None),
            ("2",    1, 7, 1, "digit", None),
            ("3",    2, 7, 1, "digit", None),
            ("+/-",  3, 7, 1, "special", self._on_negate),
            (".",    4, 7, 1, "digit",  None),

            # ── Row 8: zero and equals ──
            ("0",    0, 8, 2, "digit",  None),
            ("=",    2, 8, 3, "equals", self._on_evaluate),
        ]

        for text, col, row, colspan, btn_type, action in buttons:
            bg = COLORS.get(f"{btn_type}_bg", "#313244")
            fg = COLORS.get(f"{btn_type}_fg", "#cdd6f4")

            btn = tk.Button(
                self,
                text=text,
                font=("Consolas", 14, "bold"),
                bg=bg,
                fg=fg,
                activebackground=self._lighten(bg),
                activeforeground=fg,
                relief="flat",
                borderwidth=0,
                padx=6,
                pady=12,
                command=action if action else lambda t=text: self._handle_button(t),
            )
            btn.grid(
                row=row, column=col,
                columnspan=colspan,
                sticky="nsew",
                padx=2, pady=2,
            )

            if text == "DEG":
                self._mode_button = btn

        # Make all columns/rows expand equally
        for c in range(5):
            self.columnconfigure(c, weight=1, uniform="col")
        for r in range(9):
            self.rowconfigure(r, weight=1, uniform="row")

    def _handle_button(self, text: str):
        """Map button label to the token string sent to the controller."""
        token_map = {
            "sin":  "sin(",
            "cos":  "cos(",
            "tan":  "tan(",
            "asin": "asin(",
            "acos": "acos(",
            "atan": "atan(",
            "sinh": "sinh(",
            "cosh": "cosh(",
            "tanh": "tanh(",
            "√":    "sqrt(",
            "ln":   "ln(",
            "log":  "log(",
            "eˣ":   "exp(",
            "|x|":  "abs(",
            "x²":   "^2",
            "x!":   "!",
            "π":    "pi",
        }
        token = token_map.get(text, text)
        self._on_input(token)

    def update_mode_label(self, label: str):
        """Update the DEG/RAD button text."""
        if self._mode_button:
            self._mode_button.configure(text=label)

    @staticmethod
    def _lighten(hex_color: str, factor: float = 0.15) -> str:
        """Return a slightly lighter version of a hex colour."""
        hex_color = hex_color.lstrip('#')
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"