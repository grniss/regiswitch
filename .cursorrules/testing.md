# Test Structure Convention

## Rule 1: Every Function and Class Must Have a Unit Test

Every public function and every class (including its public methods) **must have at least one corresponding unit test**. This is non-negotiable when adding or modifying source code.

### What requires a test
- Every `def` at module level
- Every method inside a `class` (except `__init__` unless it has non-trivial logic)
- Edge cases and error paths (invalid input, exceptions raised, empty collections, etc.)

### Test naming inside the file
```python
# Source: commands/deploy.py
def run_deploy(env): ...
class Deployer:
    def execute(self): ...
    def rollback(self): ...

# Test: tests/test_commands/test_deploy.py
def test_run_deploy_success(): ...
def test_run_deploy_invalid_env(): ...   # edge case

class TestDeployer:
    def test_execute(): ...
    def test_rollback(): ...
```

---

## Rule 2: Mirror Source Directory Structure in Tests

When creating new test files, always inspect the existing project and test directory structure first, then mirror it consistently.

---

## Core Principle

The test directory structure **must mirror** the source directory structure. Never flatten nested source paths into a single filename.

---

## How to Determine the Correct Test Path

### Step 1 — Scan the existing test directory
Before creating any test file, list what already exists:
```
tests/
├── test_cores/          ← mirrors cores/
│   └── test_utils.py
```

### Step 2 — Identify the pattern
From the example above, the pattern is:
- Source folder `cores/` → Test folder `test_cores/`
- Source file `cores/utils.py` → Test file `tests/test_cores/test_utils.py`

### Step 3 — Apply the same pattern to new modules
For a new file `commands/deploy.py`, follow the same convention:
- Source folder `commands/` → Test folder `test_commands/`
- Source file `commands/deploy.py` → Test file `tests/test_commands/test_deploy.py`

---

## Naming Rules

| Source path | ✅ Correct test path | ❌ Wrong test path |
|---|---|---|
| `cores/parser.py` | `tests/test_cores/test_parser.py` | `tests/test_cores_parser.py` |
| `commands/deploy.py` | `tests/test_commands/test_deploy.py` | `tests/test_commands_deploy.py` |
| `commands/auth/login.py` | `tests/test_commands/test_auth/test_login.py` | `tests/test_commands_auth_login.py` |
| `utils/helpers.py` | `tests/test_utils/test_helpers.py` | `tests/test_utils_helpers.py` |

**Summary of naming rules:**
- Each source directory `<name>/` maps to a test directory `test_<name>/`
- Each source file `<name>.py` maps to a test file `test_<name>.py`
- Nesting is preserved at every level — never collapse path segments into underscores

---

## Decision Flow

```
Want to add a test for src/commands/deploy.py?
        │
        ▼
Scan tests/ directory
        │
        ▼
Does test_commands/ exist?
   ├── YES → Create tests/test_commands/test_deploy.py
   └── NO  → Create test_commands/ directory first,
              then create tests/test_commands/test_deploy.py
```

---

## Always Include an `__init__.py`

When creating a new test subdirectory, add an empty `__init__.py`:
```
tests/
└── test_commands/
    ├── __init__.py       ← required
    └── test_deploy.py
```

---

## Examples

### ✅ Correct
```
# Source: commands/deploy.py
# Test:
tests/test_commands/test_deploy.py
```

```
# Source: commands/auth/login.py
# Test:
tests/test_commands/test_auth/test_login.py
```

### ❌ Wrong
```
# Source: commands/deploy.py
# Do NOT do this:
tests/test_commands_deploy.py
tests/commands_test.py
tests/deploy_test.py
```

---

## Before Writing Any Test — Checklist

- [ ] Listed the existing `tests/` directory structure
- [ ] Identified the naming pattern already in use
- [ ] Created the mirrored subdirectory if it doesn't exist
- [ ] Added `__init__.py` to any new test subdirectory
- [ ] Named the file `test_<source_filename>.py` inside the correct folder
- [ ] Every public function in the source file has at least one test
- [ ] Every public class method has at least one test
- [ ] At least one edge case or error path is covered per function/method