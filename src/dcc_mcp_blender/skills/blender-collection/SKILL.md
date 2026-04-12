---
name: blender-collection
description: "Blender collection management — create, link objects, and organize scene hierarchy"
dcc: blender
version: "1.0.0"
tags: [blender, collection, hierarchy, organization]
search-hint: "collection, group, organize, hierarchy"
license: "MIT"
allowed-tools: ["Bash", "Read"]
depends: []
tools:
  - name: create_collection
    description: "Create a new collection in the scene"
    source_file: scripts/create_collection.py
    read_only: false
    destructive: false
    idempotent: false
  - name: link_to_collection
    description: "Link an object to a collection"
    source_file: scripts/link_to_collection.py
    read_only: false
    destructive: false
    idempotent: true
  - name: list_collections
    description: "List all collections in the scene"
    source_file: scripts/list_collections.py
    read_only: true
    destructive: false
    idempotent: true
---

# blender-collection

Blender collection management skill.
