---
name: blender-render
description: "Blender rendering — render scenes, set render settings, manage cameras"
dcc: blender
version: "1.0.0"
tags: [blender, render, camera]
search-hint: "render, output, resolution, camera, cycles, eevee"
license: "MIT"
allowed-tools: ["Bash", "Read"]
depends: []
tools:
  - name: render_scene
    description: "Render the current scene and save to a file"
    source_file: scripts/render_scene.py
    read_only: false
    destructive: false
    idempotent: false
  - name: set_render_settings
    description: "Configure render settings (engine, resolution, samples, output path)"
    source_file: scripts/set_render_settings.py
    read_only: false
    destructive: false
    idempotent: true
  - name: get_render_info
    description: "Return current render settings"
    source_file: scripts/get_render_info.py
    read_only: true
    destructive: false
    idempotent: true
---

# blender-render

Blender rendering skill.
