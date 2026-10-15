"""Validates every PBIP JSON file against Microsoft's published schemas.

Usage: python validate_pbip.py <pbip folder>
Schemas are downloaded from github.com/microsoft/json-schemas on first use and cached in %TEMP%/pbip_schemas.
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

from jsonschema import Draft7Validator
from referencing import Registry, Resource

CACHE = Path(os.environ.get("TEMP", "/tmp")) / "pbip_schemas"
PREFIX = "https://developer.microsoft.com/json-schemas/"
RAW = "https://raw.githubusercontent.com/microsoft/json-schemas/main/"


def retrieve(uri):
    rel = uri.replace(PREFIX, "").split("#")[0]
    local = CACHE / rel
    if not local.exists():
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_bytes(urllib.request.urlopen(RAW + rel).read())
    return Resource.from_contents(json.loads(local.read_text(encoding="utf-8")))


registry = Registry(retrieve=retrieve)
root = Path(sys.argv[1])
errors = 0
for f in sorted(root.rglob("*")):
    if f.suffix not in (".json", ".pbir", ".pbism", ".pbip") or "StaticResources" in f.parts or ".pbi" in f.parts:
        continue
    doc = json.loads(f.read_text(encoding="utf-8"))
    if "$schema" not in doc:
        continue
    errs = list(Draft7Validator(retrieve(doc["$schema"]).contents, registry=registry).iter_errors(doc))
    errors += len(errs)
    if errs:
        print("FAIL", f.relative_to(root))
        for e in errs[:5]:
            print("     ", list(e.absolute_path), e.message[:300])
print("files checked; errors:", errors)
sys.exit(1 if errors else 0)
