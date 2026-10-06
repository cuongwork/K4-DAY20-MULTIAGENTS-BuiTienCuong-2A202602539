### Human
The test suite of the `inventory` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: grep
{"pattern": "def ", "path": "workspace/inventory"}

### Tool result
/workspace/inventory/export.py
/workspace/inventory/pricing.py
/workspace/inventory/report.py

### Tool call: read_file
{"file_path": "/workspace/inventory/export.py"}

### Tool call: read_file
{"file_path": "/workspace/inventory/pricing.py"}

### Tool call: read_file
{"file_path": "/workspace/inventory/report.py"}

### Tool result
@@ lines 1-12 of 12 @@
"""Export helpers."""
from .pricing import parse_price


def to_csv_row(item):
    """Format one item as a CSV row: name,price,qty (price with 2 decimals).

    A name that contains a comma or a double quote is wrapped in double quotes,
    and every double quote inside it is doubled (RFC 4180).
    """
    price = parse_price(item["price"])
    return f'{item["name"]},{price:.2f},{item["qty"]}'

### Tool result
@@ lines 1-25 of 25 @@
"""Price utilities for the inventory package."""
from decimal import Decimal


def parse_price(text):
    """Convert a price string to a Decimal.

    Supported formats:
      "$1,299.50" -> Decimal("1299.50")
      "  12 "     -> Decimal("12")
      "1299.5"    -> Decimal("1299.5")
      "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
    """
    cleaned = text.strip().replace("$", "")
    return Decimal(cleaned)


def apply_discount(price, percent):
    """Return `price` after a percentage discount.

    The result is a Decimal rounded to 2 decimal places using the
    commercial rule "round half up" (0.005 -> 0.01).
    """
    discounted = price * (100 - percent) / 100
    return discounted.quantize(Decimal("0.01"))

### Tool result
@@ lines 1-25 of 25 @@
"""Inventory reports."""
from decimal import Decimal

from .pricing import apply_discount, parse_price


def total_value(items):
    """Total value of `items` after per-item discounts.

    Each item is a dict: {"name": str, "price": str, "qty": int, "discount": percent (optional)}.
    """
    total = Decimal("0")
    for item in items:
        price = parse_price(item["price"])
        price = apply_discount(price, item.get("discount", 0))
        total += price * item["qty"]
    return total


def low_stock(items, threshold=5):
    """Names of the items whose quantity is strictly below `threshold`.

    The names are sorted alphabetically, ignoring case.
    """
    return [item["name"] for item in items if item["qty"] <= threshold]

### Tool call: read_file
{"file_path": "/workspace/inventory/export.py", "offset": 12, "limit": 20}

### Tool result
Error: Line offset 12 exceeds file length (12 lines)

### Tool call: read_file
{"file_path": "/workspace/inventory/pricing.py", "offset": 25, "limit": 20}

### Tool result
Error: Line offset 25 exceeds file length (25 lines)

### Tool call: read_file
{"file_path": "/workspace/inventory/report.py", "offset": 25, "limit": 20}

### Tool result
Error: Line offset 25 exceeds file length (25 lines)

### Tool call: read_file
{"file_path": "/workspace/inventory/export.py", "offset": 0, "limit": 12}

### Tool result
@@ lines 1-12 of 12 @@
"""Export helpers."""
from .pricing import parse_price


def to_csv_row(item):
    """Format one item as a CSV row: name,price,qty (price with 2 decimals).

    A name that contains a comma or a double quote is wrapped in double quotes,
    and every double quote inside it is doubled (RFC 4180).
    """
    price = parse_price(item["price"])
    return f'{item["name"]},{price:.2f},{item["qty"]}'

### Tool call: read_file
{"file_path": "/workspace/inventory/pricing.py", "offset": 0, "limit": 25}

### Tool result
@@ lines 1-25 of 25 @@
"""Price utilities for the inventory package."""
from decimal import Decimal


def parse_price(text):
    """Convert a price string to a Decimal.

    Supported formats:
      "$1,299.50" -> Decimal("1299.50")
      "  12 "     -> Decimal("12")
      "1299.5"    -> Decimal("1299.5")
      "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
    """
    cleaned = text.strip().replace("$", "")
    return Decimal(cleaned)


def apply_discount(price, percent):
    """Return `price` after a percentage discount.

    The result is a Decimal rounded to 2 decimal places using the
    commercial rule "round half up" (0.005 -> 0.01).
    """
    discounted = price * (100 - percent) / 100
    return discounted.quantize(Decimal("0.01"))

### Tool call: read_file
{"file_path": "/workspace/inventory/report.py", "offset": 0, "limit": 25}

### Tool result
@@ lines 1-25 of 25 @@
"""Inventory reports."""
from decimal import Decimal

from .pricing import apply_discount, parse_price


def total_value(items):
    """Total value of `items` after per-item discounts.

    Each item is a dict: {"name": str, "price": str, "qty": int, "discount": percent (optional)}.
    """
    total = Decimal("0")
    for item in items:
        price = parse_price(item["price"])
        price = apply_discount(price, item.get("discount", 0))
        total += price * item["qty"]
    return total


def low_stock(items, threshold=5):
    """Names of the items whose quantity is strictly below `threshold`.

    The names are sorted alphabetically, ignoring case.
    """
    return [item["name"] for item in items if item["qty"] <= threshold]

### Assistant
I found several issues in the source code that cause the test suite to fail and do not meet the docstring specifications:

1. In export.py, the function to_csv_row does not handle names containing commas or double quotes correctly. It should wrap such names in double quotes and double any internal double quotes according to RFC 4180.

2. In pricing.py, the parse_price function does not handle commas in the price string (e.g., "$1,299.50") and does not handle parentheses for negative values as described in the docstring.

3. In pricing.py, the apply_discount function does not round using the "round half up" commercial rule as specified.

4. In report.py, the low_stock function includes items with quantity less than or equal to the threshold, but the docstring says strictly below the threshold. Also, the returned names are not sorted alphabetically ignoring case.

I will fix these issues accordingly.

### Tool call: edit_file
{"file_path": "/workspace/inventory/export.py", "old_string": "    price = parse_price(item[\"price\"])\n    return f'{item[\"name\"]},{price:.2f},{item[\"qty\"]}'", "new_string": "    price = parse_price(item[\"price\"])\n    name = item[\"name\"]\n    if ',' in name or '\"' in name:\n        name = '\"' + name.replace('\"', '\"\"') + '\"'\n    return f'{name},{price:.2f},{item[\"qty\"]}'"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/export.py'

### Tool call: edit_file
{"file_path": "/workspace/inventory/pricing.py", "old_string": "    cleaned = text.strip().replace(\"$\", \"\")\n    return Decimal(cleaned)", "new_string": "    cleaned = text.strip().replace(\"$\", \"\").replace(\",\", \"\")\n    if cleaned.startswith(\"(\") and cleaned.endswith(\")\"):\n        cleaned = \"-\" + cleaned[1:-1]\n    return Decimal(cleaned)"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/pricing.py'

### Tool call: edit_file
{"file_path": "/workspace/inventory/pricing.py", "old_string": "    discounted = price * (100 - percent) / 100\n    return discounted.quantize(Decimal(\"0.01\"))", "new_string": "    from decimal import ROUND_HALF_UP\n    discounted = price * (100 - percent) / 100\n    return discounted.quantize(Decimal(\"0.01\"), rounding=ROUND_HALF_UP)"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/pricing.py'

### Tool call: edit_file
{"file_path": "/workspace/inventory/report.py", "old_string": "    return [item[\"name\"] for item in items if item[\"qty\"] <= threshold]", "new_string": "    names = [item[\"name\"] for item in items if item[\"qty\"] < threshold]\n    return sorted(names, key=lambda n: n.lower())"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/report.py'

### Tool call: execute
{"command": "pytest --maxfail=1 --disable-warnings -q workspace/tests"}

### Tool result

==================================== ERRORS ====================================
_______________ ERROR collecting workspace/tests/test_report.py ________________
ImportError while importing test module '/tmp/lab-gm92gzig/workspace/tests/test_report.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/local/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
workspace/tests/test_report.py:3: in <module>
    from inventory.export import to_csv_row
E   ModuleNotFoundError: No module named 'inventory'
=========================== short test summary info ============================
ERROR workspace/tests/test_report.py
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.12s

Exit code: 2
[Command failed with exit code 2]

### Tool call: execute
{"command": "PYTHONPATH=workspace pytest --maxfail=1 --disable-warnings -q workspace/tests"}

### Tool result
......                                                                   [100%]
6 passed in 0.01s

[Command succeeded with exit code 0]

### Assistant
I fixed the following issues in the source code:

- In export.py, to_csv_row now correctly wraps names containing commas or double quotes in double quotes and doubles internal double quotes as per RFC 4180.
- In pricing.py, parse_price now removes commas and handles parentheses for negative values as specified.
- In pricing.py, apply_discount now rounds using the "round half up" commercial rule.
- In report.py, low_stock now returns names of items with quantity strictly below the threshold, sorted alphabetically ignoring case.

After these fixes, the full test suite passes successfully.