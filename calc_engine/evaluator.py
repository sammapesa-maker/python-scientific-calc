"""
Expression evaluator.

Takes a raw expression string (as built by the GUI),
sanitises it, transforms it into evaluable Python, and
computes the result inside a restricted namespace.
"""

import re
import math

from .functions import (
    AngleMode,
    safe_sqrt, safe_factorial, safe_abs,
    safe_ln, safe_log10, safe_exp, safe_power,
    safe_sinh, safe_cosh, safe_tanh,
    make_sin, make_cos, make_tan,
    make_asin, make_acos, make_atan,
)
from .exceptions import (
    CalculatorError,
    DivisionByZeroError,
    InvalidExpressionError,
    ParenthesisMismatchError,
    OverflowCalculationError,
)


# Characters and names that are permitted in an expression
_ALLOWED_NAMES = {
    "sin", "cos", "tan",
    "asin", "acos", "atan",
    "sinh", "cosh", "tanh",
    "sqrt", "abs", "ln", "log",
    "exp", "factorial",
    "pi", "e",
    "pow",
}

# Regex: only digits, whitespace, operators, parens, dots, and allowed names
_TOKEN_PATTERN = re.compile(
    r'^[\d\s\+\-\*\/\%\.\(\)\,\^]*$'
)


class ExpressionEvaluator:
    """Stateless evaluator — call evaluate() with expression + angle mode."""

    # ──────────────────────────────────────
    #  Public API
    # ──────────────────────────────────────

    def evaluate(self, expression: str, angle_mode: AngleMode = AngleMode.RAD) -> float:
        """
        Evaluate a mathematical expression string.

        Parameters
        ----------
        expression : str
            Raw expression, e.g. "sin(45)+2^3"
        angle_mode : AngleMode
            DEG or RAD — affects trig functions.

        Returns
        -------
        float

        Raises
        ------
        CalculatorError (or subclass) on any invalid input.
        """
        if not expression or expression.isspace():
            raise InvalidExpressionError("empty expression")

        self._check_parentheses(expression)

        transformed = self._transform(expression)
        self._validate(transformed)
        namespace = self._build_namespace(angle_mode)

        try:
            result = eval(transformed, {"__builtins__": {}}, namespace)  # noqa: S307
        except ZeroDivisionError:
            raise DivisionByZeroError()
        except OverflowError:
            raise OverflowCalculationError()
        except CalculatorError:
            raise  # already a well-formed error
        except Exception as exc:
            raise InvalidExpressionError(str(exc)) from exc

        if isinstance(result, complex):
            raise InvalidExpressionError("complex numbers are not supported")
        if math.isinf(result):
            raise OverflowCalculationError()
        if math.isnan(result):
            raise InvalidExpressionError("result is undefined")

        return float(result)

    # ──────────────────────────────────────
    #  Parenthesis check
    # ──────────────────────────────────────

    @staticmethod
    def _check_parentheses(expression: str):
        depth = 0
        for ch in expression:
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            if depth < 0:
                raise ParenthesisMismatchError()
        if depth != 0:
            raise ParenthesisMismatchError()

    # ──────────────────────────────────────
    #  Expression transformation
    # ──────────────────────────────────────

    @staticmethod
    def _transform(expression: str) -> str:
        """
        Transform the GUI expression into valid Python.

        Handles:
        - ^ → **
        - implicit multiplication: 2sin(… , )(, 2(, )2, pi(, e(, )pi
        - factorial postfix: number! → factorial(number)
        - × → *   ÷ → /
        - π → pi
        """
        expr = expression.strip()

        # Unicode replacements
        expr = expr.replace('×', '*')
        expr = expr.replace('÷', '/')
        expr = expr.replace('π', 'pi')

        # Handle factorial: we need to find patterns like "5!" or "(expr)!"
        # Replace number! with factorial(number)
        # Replace )! with ) and wrap the preceding parenthesised expression
        expr = ExpressionEvaluator._transform_factorial(expr)

        # Replace ^ with ** for exponentiation
        expr = expr.replace('^', '**')

        # Implicit multiplication insertion
        expr = ExpressionEvaluator._insert_implicit_multiplication(expr)

        return expr

    @staticmethod
    def _transform_factorial(expr: str) -> str:
        """Replace factorial notation (!) with factorial() function calls."""
        # Handle "number!" → "factorial(number)"
        expr = re.sub(
            r'(\d+\.?\d*)!',
            r'factorial(\1)',
            expr
        )
        # Handle ")!" → the closing paren's matching group wrapped in factorial()
        # For simplicity, handle ")!" by finding the matching "("
        while ')!' in expr:
            idx = expr.index(')!')
            # Walk backwards to find the matching '('
            depth = 0
            start = idx
            for i in range(idx, -1, -1):
                if expr[i] == ')':
                    depth += 1
                elif expr[i] == '(':
                    depth -= 1
                if depth == 0:
                    start = i
                    break
            if depth != 0:
                break  # malformed — let the parenthesis checker catch it
            inner = expr[start:idx + 1]  # includes parens
            expr = expr[:start] + f'factorial{inner}' + expr[idx + 2:]
        return expr

    @staticmethod
    def _insert_implicit_multiplication(expr: str) -> str:
        """
        Insert '*' where multiplication is implied.

        Cases:
          2sin  → 2*sin      digit followed by letter
          )2    → )*2        ) followed by digit
          )(    → )*(        ) followed by (
          2(    → 2*(        digit followed by (
          )sin  → )*sin      ) followed by letter
          pi(   → pi*(       constant/name followed by (  [handled selectively]
          pie   → pi*e       constant followed by constant
        """
        func_names = sorted(_ALLOWED_NAMES, key=len, reverse=True)
        name_pattern = '|'.join(re.escape(n) for n in func_names)

        # digit followed by letter/opening-paren
        expr = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', expr)

        # ) followed by digit, letter, or (
        expr = re.sub(r'\)(\d)', r')*\1', expr)
        expr = re.sub(r'\)([a-zA-Z])', r')*\1', expr)
        expr = re.sub(r'\)\(', r')*(', expr)

        # pi or e followed by ( — but NOT function names followed by (
        # e.g., "pi(" → "pi*(" but "sin(" stays "sin("
        constants = {'pi', 'e'}
        for const in constants:
            # const followed by ( where const is not part of a longer function name
            pattern = rf'(?<![a-zA-Z])({re.escape(const)})(\()'
            # Only insert * if the const is not a function name
            expr = re.sub(pattern, r'\1*\2', expr)

        # Fix: remove accidental * insertion inside function names
        # e.g., "exp" might become "e*xp" due to the digit rule
        # Rebuild: replace known function names that got mangled
        for name in func_names:
            if len(name) > 1:
                mangled = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', name)
                if mangled != name:
                    expr = expr.replace(mangled, name)
                # Also fix letter*letter inside function names
                mangled2 = '*'.join(name)
                if mangled2 in expr:
                    expr = expr.replace(mangled2, name)

        return expr

    # ──────────────────────────────────────
    #  Validation
    # ──────────────────────────────────────

    @staticmethod
    def _validate(transformed_expr: str):
        """
        Check that the transformed expression contains only
        allowed characters and names.
        """
        # Remove all known function/constant names first
        temp = transformed_expr
        for name in sorted(_ALLOWED_NAMES, key=len, reverse=True):
            temp = temp.replace(name, '')

        # What remains should be only digits, operators, parens, dots, whitespace
        if not re.match(r'^[\d\s\+\-\*\/\%\.\(\)\,]*$', temp):
            # Find the offending character for a useful message
            bad = re.search(r'[^\d\s\+\-\*\/\%\.\(\)\,]', temp)
            char = bad.group() if bad else '?'
            raise InvalidExpressionError(f"unexpected character: '{char}'")

    # ──────────────────────────────────────
    #  Namespace builder
    # ──────────────────────────────────────

    @staticmethod
    def _build_namespace(angle_mode: AngleMode) -> dict:
        """
        Build the dict of names available during eval().
        Trig closures are rebuilt every call so they capture
        the current angle_mode.
        """
        return {
            # Trig (angle-mode aware)
            "sin":  make_sin(angle_mode),
            "cos":  make_cos(angle_mode),
            "tan":  make_tan(angle_mode),
            "asin": make_asin(angle_mode),
            "acos": make_acos(angle_mode),
            "atan": make_atan(angle_mode),
            # Hyperbolic
            "sinh": safe_sinh,
            "cosh": safe_cosh,
            "tanh": safe_tanh,
            # Other functions
            "sqrt":      safe_sqrt,
            "factorial": safe_factorial,
            "abs":       safe_abs,
            "ln":        safe_ln,
            "log":       safe_log10,
            "exp":       safe_exp,
            "pow":       safe_power,
            # Constants
            "pi": math.pi,
            "e":  math.e,
        }