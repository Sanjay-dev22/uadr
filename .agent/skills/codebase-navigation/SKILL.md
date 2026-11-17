---
name: codebase-navigation
description: Locate the code relevant to a task quickly with targeted search instead of broad reading. Use when you need to find where behaviour lives, how a request flows, or an existing pattern to follow.
---
# Codebase navigation

1. Start from the module registry: `python3 .automation/uadr.py route <type> --path <dir>` gives the module doc, which lists entry points and important files.
2. Search before reading. Good anchors: user-visible strings, error messages, route paths, configuration keys, table names, and domain terms from the task.
3. From an anchor, follow the flow in both directions: who calls this, and what does it call. Stop at the module boundary unless the task crosses it.
4. Find the nearest existing example of what you are about to build and note its files; that set is your template.
5. Read tests for the area; they show intended behaviour and how to exercise the code.
6. Read whole files only when you will edit them. For others, read the relevant function and its signature.
7. Keep a short list of the files that matter and why. If the list passes roughly ten files, narrow the task or split it.

If the module doc was missing or wrong about where things are, fix it as part of the task.
