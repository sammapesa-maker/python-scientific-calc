# Scientific Calculator (Python + Tkinter)

A desktop scientific calculator written in Python using Tkinter. Built using a modular **Model-View-Controller (MVC)** design pattern with strict input sanitisation and safe mathematical evaluation.

---

## Features

- **Basic Arithmetic**: Addition (`+`), subtraction (`-`), multiplication (`×`), division (`÷`), modulo (`%`), powers (`^`, `x²`).
- **Scientific Functions**:
  - Trigonometry: `sin`, `cos`, `tan`
  - Inverse Trigonometry: `asin`, `acos`, `atan`
  - Hyperbolic: `sinh`, `cosh`, `tanh`
  - Logarithms: Natural Log (`ln`), Base-10 Log (`log`)
  - Exponential: `eˣ`
  - Other: Square root (`√`), Factorial (`x!`), Absolute value (`|x|`)
- **Constants**: $\pi$ (`pi`), $e$
- **Angle Units**: Toggle seamlessly between **Degrees (DEG)** and **Radians (RAD)** for all trigonometric operations.
- **Answer Chaining**: Performing an operation directly after pressing `=` chains the previous result into the new calculation.
- **Smart Backspace**: Deletes entire function tokens (e.g., `sin(`) as single units.
- **Keyboard Support**: Full numpad and keyboard shortcuts for quick calculations.
- **Error Handling**: Gracefully handles division by zero, invalid domains (e.g., $\sqrt{-1}$, $\ln(0)$), and unbalanced parentheses with inline error messaging.

---

## Design & Architecture

The application is structured in three strictly decoupled layers:

1. **Model (`calc_engine/`)**: Pure computation library. Contains safe mathematical wrappers around Python's `math` module, custom exception types, and an expression evaluator that parses and executes math inside a restricted namespace.
2. **Controller (`controller.py`)**: Manages the application state, token buffer, angle mode toggle, input sanitisation, and result formatting.
3. **View (`gui/`)**: Presentation layer built with Tkinter. Displays a two-line output (expression and result) with dynamic font scaling for error messages and a structured button grid.

---

## Project Structure

```text
python-scientific-calc/
│
├── main.py                 # Application entry point
├── controller.py           # Controller (mediates View and Model)
│
├── calc_engine/            # Model (pure math & evaluation logic)
│   ├── __init__.py
│   ├── exceptions.py       # Custom calculator exceptions
│   ├── functions.py        # Safe wrappers for math operations
│   └── evaluator.py        # Token pre-processing & safe evaluation
│
└── gui/                    # View (Tkinter UI)
    ├── __init__.py
    ├── calculator_app.py   # Main window & keyboard event binding
    ├── display.py          # Two-line display widget with dynamic sizing
    └── button_panel.py     # Grid layout & button theming
```

---

## Requirements

- Python 3.10+
- Python standard library (`math`, `re`, `enum`, `tkinter`)
- **No external `pip` dependencies required.**

### Linux (Debian / Ubuntu) Tkinter Setup

If `tkinter` is not installed on your system, install it via:

```bash
sudo apt update
sudo apt install python3-tk
```

---

## How to Run

Navigate to the project root directory and execute:

```bash
python3 main.py
```

---

## Keyboard Shortcuts

| Key                | Function          |
| ------------------ | ----------------- |
| `0` – `9`          | Digit input       |
| `+`, `-`, `*`, `/` | Basic operators   |
| `^`                | Exponentiation    |
| `(`, `)`           | Parentheses       |
| `.`                | Decimal point     |
| `Enter` / `Return` | Evaluate (`=`)    |
| `Backspace`        | Delete last token |
| `Escape`           | Clear all (`C`)   |

## Licence

This project is licensed under the MIT License