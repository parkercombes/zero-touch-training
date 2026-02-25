#!/usr/bin/env python3
"""Quick check — list all video-capable models on this API key."""
import os, sys
from pathlib import Path

def load_google_key():
    key = os.environ.get("GOOGLE_API_KEY", "")
    if key:
        return key
    for ep in [Path(__file__).parent.parent / ".env", Path(".env")]:
        if ep.exists():
            for line in ep.read_text().splitlines():
                if line.startswith("GOOGLE_API_KEY="):
                    val = line.split("=", 1)[1].strip()
                    if val:
                        return val
    return None

key = load_google_key()
if not key:
    print("ERROR: GOOGLE_API_KEY not found in poc/.env")
    sys.exit(1)

from google import genai
client = genai.Client(api_key=key)

print("All models with video generation support:\n")
found = []
for m in client.models.list():
    name = m.name
    actions = [a for a in (m.supported_actions or []) if "video" in a.lower() or "generate" in a.lower()]
    if "veo" in name.lower() or actions:
        found.append((name, actions))
        print(f"  {name}")
        if actions:
            print(f"    actions: {actions}")

if not found:
    print("  (none — this key does not have access to any video generation models)")
    print("\nAll available models:")
    for m in client.models.list():
        print(f"  {m.name}")
