"""Display widget — expression line + result line."""

import tkinter as tk


class Display(tk.Frame):
    """Two-line calculator display."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg="#1e1e2e")

        # Expression line (top, smaller)
        self._expression_var = tk.StringVar(value="")
        self._expression_label = tk.Label(
            self,
            textvariable=self._expression_var,
            font=("Consolas", 16),
            fg="#a6adc8",
            bg="#1e1e2e",
            anchor="e",
            padx=15,
        )
        self._expression_label.pack(fill="x", pady=(10, 0))

        # Result line (bottom, larger)
        self._result_var = tk.StringVar(value="0")
        self._result_label = tk.Label(
            self,
            textvariable=self._result_var,
            font=("Consolas", 28, "bold"),
            fg="#cdd6f4",
            bg="#1e1e2e",
            anchor="e",
            padx=15,
        )
        self._result_label.pack(fill="x", pady=(0, 10))

    def update_display(self, expression: str, result: str):
        """Called by the controller callback."""
        self._expression_var.set(expression)

        if result:
            # If it's an error message, reduce font size and change colour
            if result.startswith("Error:"):
                self._result_label.configure(
                    font=("Consolas", 16, "bold"),
                    fg="#f38ba8"  # Pastel Red
                )
            else:
                self._result_label.configure(
                    font=("Consolas", 28, "bold"),
                    fg="#cdd6f4"  # Default light-grey
                )
            self._result_var.set(result)
        elif not expression:
            self._result_label.configure(
                font=("Consolas", 28, "bold"),
                fg="#cdd6f4"
            )
            self._result_var.set("0")

    def get_expression(self) -> str:
        return self._expression_var.get()