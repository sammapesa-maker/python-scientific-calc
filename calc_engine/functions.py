"""
Safe wrappers around math module functions.

Every wrapper validates its input and raises DomainError
with a human-readable message when the input is outside
the function's mathematical domain.

Trigonometric wrappers accept an angle_mode parameter
("DEG" or "RAD") and convert internally.
"""

import math
from enum import Enum

from .exceptions import DomainError, OverflowCalculationError


class AngleMode(Enum):
    DEG = "DEG"
    RAD = "RAD"


# ──────────────────────────────────────────────
#  Helper: degree → radian conversion
# ──────────────────────────────────────────────

def _to_radians(x, angle_mode):
    """Convert x to radians if angle_mode is DEG."""
    if angle_mode == AngleMode.DEG:
        return math.radians(x)
    return x


def _to_degrees_result(x, angle_mode):
    """Convert a radian result back to degrees if needed (for inverse trig)."""
    if angle_mode == AngleMode.DEG:
        return math.degrees(x)
    return x


# ──────────────────────────────────────────────
#  Basic math wrappers
# ──────────────────────────────────────────────

def safe_sqrt(x):
    """Square root. Domain: x >= 0."""
    if x < 0:
        raise DomainError("√", "cannot take square root of a negative number")
    return math.sqrt(x)


def safe_factorial(x):
    """Factorial. Domain: non-negative integer."""
    if x < 0:
        raise DomainError("factorial", "input must be non-negative")
    if x != int(x):
        raise DomainError("factorial", "input must be an integer")
    x = int(x)
    if x > 170:
        raise OverflowCalculationError()
    try:
        return float(math.factorial(x))
    except (ValueError, OverflowError) as exc:
        raise OverflowCalculationError() from exc


def safe_abs(x):
    """Absolute value."""
    return math.fabs(x)


def safe_ln(x):
    """Natural logarithm. Domain: x > 0."""
    if x <= 0:
        raise DomainError("ln", "input must be positive")
    return math.log(x)


def safe_log10(x):
    """Base-10 logarithm. Domain: x > 0."""
    if x <= 0:
        raise DomainError("log", "input must be positive")
    return math.log10(x)


def safe_exp(x):
    """Exponential function e^x."""
    try:
        return math.exp(x)
    except OverflowError as exc:
        raise OverflowCalculationError() from exc


def safe_power(base, exponent):
    """Safe exponentiation."""
    try:
        result = math.pow(base, exponent)
        if math.isinf(result):
            raise OverflowCalculationError()
        return result
    except OverflowError as exc:
        raise OverflowCalculationError() from exc
    except ValueError as exc:
        raise DomainError("power", str(exc)) from exc


# ──────────────────────────────────────────────
#  Trigonometric function factories
# ──────────────────────────────────────────────
#  We build closures so the evaluator can inject
#  the current angle mode before every eval call.
# ──────────────────────────────────────────────

def make_sin(angle_mode):
    def _sin(x):
        return math.sin(_to_radians(x, angle_mode))
    return _sin


def make_cos(angle_mode):
    def _cos(x):
        return math.cos(_to_radians(x, angle_mode))
    return _cos


def make_tan(angle_mode):
    def _tan(x):
        rad = _to_radians(x, angle_mode)
        # Check for values where tan is undefined (odd multiples of π/2)
        if math.isclose(math.cos(rad), 0, abs_tol=1e-10):
            raise DomainError("tan", "undefined at this value")
        return math.tan(rad)
    return _tan


# ──────────────────────────────────────────────
#  Inverse trig function factories
# ──────────────────────────────────────────────

def make_asin(angle_mode):
    def _asin(x):
        if x < -1 or x > 1:
            raise DomainError("asin", "input must be between -1 and 1")
        return _to_degrees_result(math.asin(x), angle_mode)
    return _asin


def make_acos(angle_mode):
    def _acos(x):
        if x < -1 or x > 1:
            raise DomainError("acos", "input must be between -1 and 1")
        return _to_degrees_result(math.acos(x), angle_mode)
    return _acos


def make_atan(angle_mode):
    def _atan(x):
        return _to_degrees_result(math.atan(x), angle_mode)
    return _atan


# ──────────────────────────────────────────────
#  Hyperbolic functions (no angle mode needed)
# ──────────────────────────────────────────────

def safe_sinh(x):
    try:
        return math.sinh(x)
    except OverflowError as exc:
        raise OverflowCalculationError() from exc


def safe_cosh(x):
    try:
        return math.cosh(x)
    except OverflowError as exc:
        raise OverflowCalculationError() from exc


def safe_tanh(x):
    return math.tanh(x)