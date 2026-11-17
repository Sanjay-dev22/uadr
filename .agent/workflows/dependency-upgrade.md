---
purpose: Procedure for adding, upgrading, replacing, or removing dependencies.
read_when: The router selects the dependency-upgrade route.
---
# Workflow: dependency-upgrade

## Objective

Change a dependency with known impact, passing tests, and no new vulnerabilities or licence problems.

## Required context

- Which dependency, from and to which version, and why (security, feature, end of life).

## Documents to read

- Output of `uadr.py route dependency-upgrade --path <paths>`; nothing else up front.
- Setup and build doc for the dependency tooling.

## Steps

1. Record current and target versions and whether the bump is patch, minor, or major.
2. Read the changelog or release notes between the versions for breaking changes and deprecations.
3. Find every use of the dependency in the codebase (skill: `dependency-analysis`).
4. Check licence and known advisories for the target version (skill: `security-analysis`).
5. Upgrade one dependency, or one coupled group, per change using the package manager; commit the lockfile.
6. Fix breakages at call sites; do not pin around a failure without recording it.
7. Run validation and report including notable upstream changes.

## Files that may be modified

- Dependency manifests and lockfiles.
- Call sites that must change.
- Docs listed below.

## Validation

- `python3 .automation/uadr.py run all`: every configured command passes.
- `python3 .automation/uadr.py check` passes.
- The project's vulnerability audit, if configured, reports no new findings.

## Completion criteria

- Dependency at target version; build and tests pass; impact summarised.
- Completion report delivered in the `.agent/policies/quality.md` format.

## Documentation updates

- Setup and build doc if tooling or runtime versions changed.
- Architecture technology stack for framework or runtime changes.
- `CHANGELOG.md` when users are affected.

## Human approval

- New dependency, major upgrade, licence change, or new package source.
