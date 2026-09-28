"""Custom exception hierarchy for the calculator engine."""


class CalculatorError(Exception):
    """Base exception for all calculator errors."""

    def __init__(self, message="Math Error"):
        self.message = message
        super().__init__(self.message)


class DivisionByZeroError(CalculatorError):
    """Raised when division by zero is attempted."""

    def __init__(self):
        super().__init__("Can't Divide by Zero")


class DomainError(CalculatorError):
    """Raised when a function receives an argument outside its domain."""

    def __init__(self, function_name="", reason=""):
        super().__init__("Domain Error")


class InvalidExpressionError(CalculatorError):
    """Raised when the expression string cannot be parsed."""

    def __init__(self, detail=""):
        super().__init__("Syntax Error")


class ParenthesisMismatchError(CalculatorError):
    """Raised when parentheses are not balanced."""

    def __init__(self):
        super().__init__("Parenthesis Error")


class OverflowCalculationError(CalculatorError):
    """Raised when a result is too large to represent."""

    def __init__(self):
        super().__init__("Overflow")