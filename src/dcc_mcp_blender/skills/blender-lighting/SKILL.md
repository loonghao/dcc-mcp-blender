---
name: blender-lighting
description: "Blender lighting — create, configure and manage lights"
dcc: blender
version: "1.0.0"
tags: [blender, lighting, lights]
search-hint: "create light, point, sun, area, spot, energy, color"
license: "MIT"
allowed-tools: ["Bash", "Read"]
depends: []
tools:
  - name: create_light
    description: "Create a new light object (POINT, SUN, AREA, SPOT)"
    source_file: scripts/create_light.py
    read_only: false
    destructive: false
    idempotent: false
  - name: set_light_properties
    description: "Set energy, color, and other light properties"
    source_file: scripts/set_light_properties.py
    read_only: false
    destructive: false
    idempotent: true
  - name: list_lights
    description: "List all lights in the current scene"
    source_file: scripts/list_lights.py
    read_only: true
    destructive: false
    idempotent: true
---

# blender-lighting

Blender lighting management skill.
