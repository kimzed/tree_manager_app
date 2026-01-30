
**Apply KISS (Keep It Simple, Stupid)** and avoid unnecessary verbosity.

General Guidelines

Clarity > Cleverness: Write readable, maintainable code.
Typing: Use type hints and return types everywhere except in tests.
Comments: are allowed *only* to explain intent, trade-offs, constraints or non obvious decisions. limit them as much as possible, code should be self explanatory.
Docstrings: Short, clear, and only for public functions/classes.
Error Handling: Handle only expected errors; do not use try/except otherwise.
Indentation: Avoid deep nesting. limit indentation as much as possible.

Tests:

One assert per test case. Focus on ensuring the function works properly with a realistic, logical and easy to read usecase. if there are try except test the exception is caught in a separate test. no edge case.

Do Not

Over-engineer.
Add unnecessary abstractions.
Ignore typing in src/.
Use letters for variable names.
Handle unexpected errors.
