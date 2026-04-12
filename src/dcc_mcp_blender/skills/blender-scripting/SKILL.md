---
name: blender-scripting
description: "Execute Python code or scripts inside Blender's Python interpreter"
dcc: blender
version: "1.0.0"
tags: [blender, scripting, python, automation]
search-hint: "execute python, run script, blender python, bpy"
license: "MIT"
allowed-tools: ["Bash", "Read"]
depends: []
tools:
  - name: execute_python
    description: "Execute a Python code snippet inside Blender"
    source_file: scripts/execute_python.py
    read_only: false
    destructive: false
    idempotent: false
  - name: execute_script_file
    description: "Execute a Python script file inside Blender"
    source_file: scripts/execute_script_file.py
    read_only: false
    destructive: false
    idempotent: false
  - name: get_blender_info
    description: "Get Blender version and Python environment information"
    source_file: scripts/get_blender_info.py
    read_only: true
    destructive: false
    idempotent: true
---

# blender-scripting

Execute arbitrary Python code inside Blender's Python interpreter.
