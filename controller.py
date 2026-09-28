"""
Calculator controller.

Manages application state (current expression, angle mode,
answer chaining) and mediates between the GUI and the
calculation engine.
"""

from calc_engine import ExpressionEvaluator, AngleMode, CalculatorError


class CalculatorController:
    """Central coordinator between View and Engine."""

    # Tokens that are multi-character and should be deleted as a unit
    FUNCTION_TOKENS = [
        "asin(", "acos(", "atan(",
        "sinh(", "cosh(", "tanh(",
        "sin(", "cos(", "tan(",
        "sqrt(", "ln(", "log(", "exp(",
        "factorial(", "abs(",
        "pi", "e",
    ]

    def __init__(self):
        self._engine = ExpressionEvaluator()
        self._tokens: list[str] = []        # parallel token list
        self._angle_mode = AngleMode.DEG
        self._last_result: str | None = None
        self._has_result = False             # True right after "=" is pressed

        # Callbacks the View will register
        self._display_cb = None   # fn(expression: str, result: str)
        self._mode_cb = None      # fn(mode_label: str)

    # ──────────────────────────────────────
    #  Callback registration
    # ──────────────────────────────────────

    def set_display_callback(self, callback):
        """Register fn(expression_str, result_str) for display updates."""
        self._display_cb = callback

    def set_mode_callback(self, callback):
        """Register fn(mode_label_str) for angle-mode updates."""
        self._mode_cb = callback

    # ──────────────────────────────────────
    #  Properties
    # ──────────────────────────────────────

    @property
    def expression(self) -> str:
        return ''.join(self._tokens)

    @property
    def angle_mode(self) -> AngleMode:
        return self._angle_mode

    # ──────────────────────────────────────
    #  Input handling
    # ──────────────────────────────────────

    def on_input(self, token: str):
        """
        Handle a button press.

        token can be a digit, operator, function name,
        parenthesis, decimal point, or constant.
        """
        # ── Answer chaining ──
        if self._has_result:
            if token in ('+', '-', '*', '/', '%', '^', '×', '÷'):
                # Start new expression seeded with previous result
                self._tokens = [self._last_result]
                self._has_result = False
            else:
                # Fresh expression
                self._tokens = []
                self._has_result = False

        self._tokens.append(token)
        self._update_display(self.expression, "")

    def on_evaluate(self):
        """Handle the = button."""
        expr = self.expression
        if not expr:
            return

        try:
            result = self._engine.evaluate(expr, self._angle_mode)
            result_str = self._format_result(result)
            self._last_result = result_str
            self._has_result = True
            self._update_display(expr, result_str)
        except CalculatorError as err:
            self._has_result = False
            self._update_display(expr, f"Error: {err.message}")

    def on_clear(self):
        """Handle the C button — full reset."""
        self._tokens = []
        self._has_result = False
        self._update_display("", "")

    def on_backspace(self):
        """Handle the ⌫ button — remove last logical token."""
        if self._has_result:
            # After a result, backspace clears everything
            self.on_clear()
            return
        if not self._tokens:
            return
        self._tokens.pop()
        self._update_display(self.expression, "")

    def on_toggle_angle_mode(self):
        """Toggle between DEG and RAD."""
        if self._angle_mode == AngleMode.DEG:
            self._angle_mode = AngleMode.RAD
        else:
            self._angle_mode = AngleMode.DEG

        if self._mode_cb:
            self._mode_cb(self._angle_mode.value)

    def on_negate(self):
        """Toggle the sign of the current number entry."""
        if self._has_result and self._last_result:
            # Negate the result and start fresh
            try:
                val = float(self._last_result)
                val = -val
                result_str = self._format_result(val)
                self._tokens = [result_str]
                self._last_result = result_str
                self._has_result = False
                self._update_display(self.expression, "")
            except ValueError:
                pass
            return

        if not self._tokens:
            self._tokens.append('-')
            self._update_display(self.expression, "")
            return

        # Find the last numeric sequence and negate it
        # Simple approach: if last token starts with '-', remove it; else prepend '-'
        last = self._tokens[-1]
        try:
            val = float(last)
            self._tokens[-1] = self._format_result(-val)
        except ValueError:
            # Not a simple number — just insert a minus
            self._tokens.append('-')
        self._update_display(self.expression, "")

    # ──────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────

    def _update_display(self, expression: str, result: str):
        if self._display_cb:
            self._display_cb(expression, result)

    @staticmethod
    def _format_result(value: float) -> str:
        """Format a float for display."""
        if value == float('inf') or value == float('-inf'):
            return "Overflow"

        # If it's an integer value, show without decimal
        if value == int(value) and abs(value) < 1e15:
            return str(int(value))

        # For very large or very small numbers use scientific notation
        if abs(value) >= 1e15 or (abs(value) < 1e-10 and value != 0):
            return f"{value:.6e}"

        # Otherwise show up to 10 significant figures, strip trailing zeros
        formatted = f"{value:.10g}"
        return formatted