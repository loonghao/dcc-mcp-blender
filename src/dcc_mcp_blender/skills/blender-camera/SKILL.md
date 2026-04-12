---
name: blender-camera
description: "Blender camera management — create, configure and set active cameras"
dcc: blender
version: "1.0.0"
tags: [blender, camera, viewport]
search-hint: "camera, lens, focal length, active camera, perspective"
license: "MIT"
allowed-tools: ["Bash", "Read"]
depends: []
tools:
  - name: create_camera
    description: "Create a new camera object"
    source_file: scripts/create_camera.py
    read_only: false
    destructive: false
    idempotent: false
  - name: set_active_camera
    description: "Set the active render camera for the scene"
    source_file: scripts/set_active_camera.py
    read_only: false
    destructive: false
    idempotent: true
  - name: set_camera_properties
    description: "Configure camera properties (focal length, type, etc.)"
    source_file: scripts/set_camera_properties.py
    read_only: false
    destructive: false
    idempotent: true
  - name: list_cameras
    description: "List all cameras in the scene"
    source_file: scripts/list_cameras.py
    read_only: true
    destructive: false
    idempotent: true
---

# blender-camera

Blender camera management skill.
