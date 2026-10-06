---
name: enforce-type-annotations-on-public-functions
description: Use when writing or updating package code to ensure all public functions have complete type hints.
---
1. Identify all public functions in the package (functions whose names do not start with an underscore).
2. For each public function, verify that every parameter has an explicit type annotation.
3. Verify that the return type of each public function is explicitly annotated.
4. Use standard Python typing syntax (e.g., `def func(x: int) -> str:`).
5. If a function lacks annotations, add them based on the function’s expected input and output types.
6. Avoid partial annotations; all parameters and return types must be annotated.
7. Use type hints consistent with the project’s typing conventions and imports.
8. Run static type checkers (e.g., mypy) to validate annotations before submission.
9. Document any complex types or custom classes used in annotations.
10. Review all public functions after edits to ensure no annotation is missing.