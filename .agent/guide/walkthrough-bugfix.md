---
purpose: Worked example of an agent fixing a bug through the framework, with real command output.
read_when: Human adopters wanting to see the framework in use; not needed by agents.
---
# Walkthrough: fixing a bug

The repository is a small Python order service that was onboarded in Mode B. It has two registered modules, `orders` and `pricing`, and its test command is configured. All output below was produced by running the commands.

**Task:** "Customers ordering exactly 10 units get no bulk discount; the total is wrong."

## 1. Route

The agent has `AGENTS.md` in context (561 tokens) and reads `state.md`, then routes:

```text
$ python3 .automation/uadr.py route "customers ordering exactly 10 units get no bulk discount - wrong total" --path src/shop/pricing/discounts.py
Route: bugfix - Observed behaviour differs from intended behaviour
Workflow: .agent/workflows/bugfix.md  (~508 tok)
Read first:
  - .agent/memory/state.md  (~122 tok)
  - docs/modules/pricing.md  (~286 tok)  [module: pricing]
Read only if:
  - .agent/memory/known-issues.md  <- the symptom may be a known limitation
Skills (load one only when a step needs it):
  - .agent/skills/root-cause-analysis/SKILL.md
  - .agent/skills/test-generation/SKILL.md
Human approval: Fix requires a data repair or a public contract change
```

Context so far is about 1,480 tokens. The orders module doc, the architecture docs, and the other 14 workflows are not loaded.

## 2. Understand and reproduce

The module doc states the rule: the discount applies when quantity *reaches* the threshold of 10. The workflow requires a reproduction before any change, so the agent writes a failing test in `tests/test_pricing.py`:

```python
def test_discount_applies_at_exactly_the_threshold(self):
    self.assertEqual(bulk_discount_rate(10), Decimal("0.10"))
    self.assertEqual(line_total(Decimal("2.00"), 10), Decimal("18.00"))
```

```text
$ python3 .automation/uadr.py run test
FAIL: test_discount_applies_at_exactly_the_threshold
AssertionError: Decimal('0') != Decimal('0.10')
Ran 7 tests in 0.001s
FAILED (failures=1)
RESULT test: FAILED (exit 1)
```

## 3. Root cause

The agent reads `src/shop/pricing/discounts.py` (20 lines). `bulk_discount_rate` compares with `quantity > BULK_THRESHOLD`, which excludes exactly 10. The existing tests covered 3 and 20 units but not the boundary, which is why this was never caught. A search shows `BULK_THRESHOLD` is used nowhere else, and the only caller is `line_total`.

## 4. Fix and validate

One character changes: `>` becomes `>=`. The agent also adds a test for 9 units to pin the other side of the boundary.

```text
$ python3 .automation/uadr.py run all
[test] $ PYTHONPATH=src python3 -m unittest discover -s tests
Ran 7 tests in 0.000s
OK

RESULTS (report exactly these):
  lint    not run (not configured)
  static  not run (not configured)
  build   not run (not configured)
  test    passed

$ python3 .automation/uadr.py check
uadr check: PASSED (0 error(s), 2 warning(s), 8 check(s) run)
```

## 5. Document and report

The module doc already described the intended rule, so no documentation change is needed. No memory update is needed either: nothing durable about the project changed.

```text
Summary: Bulk discount was not applied at exactly 10 units because the threshold comparison was exclusive. Made it inclusive.
Route: bugfix   Modules: pricing
Changes: src/shop/pricing/discounts.py, tests/test_pricing.py
Validation:
  test: passed (7 tests; the new boundary test failed before the fix)
  build / lint / static: not run - not configured for this project
  uadr check: passed
Docs updated: none needed - docs/modules/pricing.md already stated the intended rule
Approvals: none required
Risks and follow-ups: Orders of exactly 10 units placed before this fix were charged without the discount; whether to correct them is a business decision.
```

Two things to notice: the unconfigured commands are reported as not run rather than passed, and the agent raised the question of past orders instead of attempting a data repair, which would require approval.
