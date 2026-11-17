---
name: repository-exploration
description: Build a fast, accurate map of an unfamiliar repository - languages, entry points, layout, build and test tooling. Use when entering a repository or area for the first time, or during onboarding.
---
# Repository exploration

Goal: a one-page map, produced by sampling, not by reading everything.

1. Run `python3 .automation/uadr.py scan --stdout` for the generated inventory; treat every item as a candidate to verify.
2. Read manifests and build files first (package manifests, lockfiles, build scripts, container and CI files). They state languages, frameworks, commands, and deployable units more reliably than prose.
3. List the top two directory levels. Classify each directory: source, tests, configuration, infrastructure, generated, vendored. Ignore generated and vendored trees.
4. Find entry points: process starts (`main`, server bootstrap, CLI, job schedulers, function handlers) and what CI builds and deploys.
5. Open one representative file per major directory to learn conventions. Stop once a new file teaches nothing new.
6. Record: what the system does, how it starts, how it is built and tested, where each kind of code lives, and what you could not determine.

Output facts with the file that proves each. Mark anything unproven `UNKNOWN:`.
