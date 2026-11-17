---
purpose: Procedure for adding or changing an externally consumed interface.
read_when: The router selects the api route.
---
# Workflow: api

## Objective

Add or change an interface with a clear contract, validated input, correct authorisation, and contract tests.

## Required context

- The consumers, the contract (inputs, outputs, errors), and compatibility expectations.

## Documents to read

- Output of `uadr.py route api --path <paths>`; nothing else up front.
- Module doc and the API docs.
- Security docs if the interface handles identity or personal data.

## Steps

1. Define the contract first: operations, schemas, error cases, auth, versioning.
2. Find an existing interface of the same kind and follow its conventions for naming, errors, and validation.
3. Classify the change as additive or breaking. Breaking changes need approval and a migration path.
4. Implement boundary validation and authorisation before business logic (skill: `security-analysis`).
5. Implement the behaviour (skill: `feature-implementation`).
6. Add tests for success, validation failure, authorisation failure, and each error case (skill: `test-generation`).
7. Update the machine-readable contract (OpenAPI, schema, proto) if the project has one.
8. Run validation, update docs, and report.

## Files that may be modified

- Interface layer, handlers, schemas, and tests in the owning module.
- Contract definitions and API docs.

## Validation

- `python3 .automation/uadr.py run all`: every configured command passes.
- `python3 .automation/uadr.py check` passes.
- Contract tests cover every documented response and error.

## Completion criteria

- Contract implemented as specified and documented; existing consumers unaffected or migration approved.
- Completion report delivered in the `.agent/policies/quality.md` format.

## Documentation updates

- `docs/api/` and the machine-readable contract.
- Module doc entry points.
- `CHANGELOG.md`.

## Human approval

- Breaking change or removal; new unauthenticated or public interface.
