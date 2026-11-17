---
purpose: Worked example of an agent building a feature through the framework, with real command output.
read_when: Human adopters wanting to see the framework in use; not needed by agents.
---
# Walkthrough: building a feature

Same repository as the bug-fix walkthrough: a small Python order service onboarded in Mode B with modules `orders` and `pricing`.

**Task:** "Add support for cancelling an order." Acceptance criteria supplied with the task: an open order can be cancelled; a cancelled order accepts no new lines; cancelling twice is an error.

## 1. Route

```text
$ python3 .automation/uadr.py route "add support for cancelling an order" --path src/shop/orders/service.py
Route: feature - Build a capability that does not exist yet
Workflow: .agent/workflows/feature.md  (~607 tok)
Read first:
  - .agent/memory/state.md  (~122 tok)
  - docs/modules/orders.md  (~311 tok)  [module: orders]
  - docs/development/coding-standards.md  (not written yet - skip; create it only if this task needs it)
Skills (load one only when a step needs it):
  - .agent/skills/codebase-navigation/SKILL.md
  - .agent/skills/feature-implementation/SKILL.md
  - .agent/skills/test-generation/SKILL.md
Human approval: New external dependency, new module, or public contract change
```

The coding standards doc has not been written in this repository. The router says so and the agent carries on: conventions will come from the surrounding code. Context is about 1,600 tokens.

## 2. Understand, analyze, plan

From the module doc the agent learns that `OrderService` in `src/shop/orders/service.py` is the entry point, that `Order.status` exists with the value `open`, and that `add_line` already refuses orders that are not open. It reads `service.py` and `models.py` (about 60 lines together) and the existing tests.

Findings: the closest existing pattern is `add_line`, which fetches through `get` (raising `OrderNotFound`) and raises `ValueError` for an invalid state. The second criterion is therefore already enforced once the status changes.

Plan:

| File | Change |
| --- | --- |
| `src/shop/orders/service.py` | Add `cancel(order_id)`, following the `add_line` pattern |
| `tests/test_orders.py` | Four tests: cancel, cancelled order rejects lines, cancel twice, unknown order |
| `docs/modules/orders.md` | Entry point and business rule |

No new dependency, module, or contract break, so no approval is required. `cancel` is an additive method.

## 3. Implement and test

```python
def cancel(self, order_id: int) -> Order:
    """Cancel an open order. Cancelling twice is an error; cancelled orders accept no lines."""
    order = self.get(order_id)
    if order.status != "open":
        raise ValueError("order is not open")
    order.status = "cancelled"
    return order
```

```text
$ python3 .automation/uadr.py run all
[test] $ PYTHONPATH=src python3 -m unittest discover -s tests
Ran 11 tests in 0.000s
OK

RESULTS (report exactly these):
  lint    not run (not configured)
  static  not run (not configured)
  build   not run (not configured)
  test    passed
```

## 4. Document

The documentation policy maps "module behaviour, entry points, business rules" to the module doc. The agent adds `cancel` to the entry point row and one business rule to `docs/modules/orders.md`. The architecture is unchanged, so nothing else is touched.

```text
$ python3 .automation/uadr.py check
uadr check: PASSED (0 error(s), 2 warning(s), 8 check(s) run)
```

The two warnings are pre-existing and expected at this stage of adoption: onboarding is not yet closed out, and one legacy doc awaits review.

## 5. Report

```text
Summary: Added OrderService.cancel, which moves an open order to cancelled. Cancelled orders reject new lines through the existing open-status check.
Route: feature   Modules: orders
Changes: src/shop/orders/service.py, tests/test_orders.py, docs/modules/orders.md
Validation:
  test: passed (11 tests, 4 new)
  build / lint / static: not run - not configured for this project
  uadr check: passed (2 pre-existing warnings)
Docs updated: docs/modules/orders.md (entry point, business rule)
Approvals: none required
Risks and follow-ups: total() still returns a value for a cancelled order; ASSUMPTION: that is acceptable because no criterion covers it.
```
