---
name: blender-animation
description: "Blender animation — keyframes, frame ranges, and actions"
dcc: blender
version: "1.0.0"
tags: [blender, animation, keyframes]
search-hint: "keyframe, animation, frame range, action, timeline"
license: "MIT"
allowed-tools: ["Bash", "Read"]
depends: []
tools:
  - name: set_keyframe
    description: "Insert a keyframe on an object at the current or specified frame"
    source_file: scripts/set_keyframe.py
    read_only: false
    destructive: false
    idempotent: false
  - name: set_frame_range
    description: "Set the animation frame range (start and end frames)"
    source_file: scripts/set_frame_range.py
    read_only: false
    destructive: false
    idempotent: true
  - name: get_frame_range
    description: "Get the current animation frame range"
    source_file: scripts/get_frame_range.py
    read_only: true
    destructive: false
    idempotent: true
  - name: set_current_frame
    description: "Set the current animation frame"
    source_file: scripts/set_current_frame.py
    read_only: false
    destructive: false
    idempotent: true
---

# blender-animation

Blender animation keyframe and timeline skill.
