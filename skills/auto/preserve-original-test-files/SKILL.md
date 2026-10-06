---
name: preserve-original-test-files
description: Use when modifying or adding tests to ensure original test files remain unaltered.
---
1. Identify the directory containing test files (e.g., `tests/`).
2. Do not edit or overwrite any existing test files in this directory.
3. To add new tests, create new test files with unique names in the same directory.
4. Verify that no original test file content is changed by diffing before submission.
5. If a test fix is required, add new test functions in new files rather than modifying existing ones.
6. Confirm that the test suite runs successfully with the new tests included.
7. Document added tests clearly, referencing the bugs or features they cover.
8. Maintain consistent test file naming conventions as per project guidelines.
9. Always back up original test files before any test-related changes.
10. Review changes to ensure compliance with the rule of not modifying original test files.