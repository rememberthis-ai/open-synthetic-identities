"""Shared Replicate Flux client — the house pattern from the `genai-game-assets`
skill (augmentedmind/claude-skills), ported to stdlib-only Python (no
`requests` dependency). Used by gen_cast.py and generate.py.

Model choices: flux-1.1-pro (create), flux-kontext-pro (identity-preserving
variation via a base64 input_image), background-remover (alpha, not yet
needed by this dataset). Non-negotiable behaviors per the skill: retry on 429
using the server-suggested retry_after, poll until succeeded/failed, skip
work that already exists (callers' responsibility), space calls ~3s apart.
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPLICATE_API = "https://api.replicate.com/v1"
FLUX_CREATE = "black-forest-labs/flux-1.1-pro"
FLUX_KONTEXT = "black-forest-labs/flux-kontext-pro"

CALL_SPACING_SECS = 3


def replicate_predict(model_path: str, input_data: dict) -> bytes:
    """POST a prediction, handle 429/retry_after, poll to completion, fetch
    the output image bytes."""
    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        sys.exit("REPLICATE_API_TOKEN not set")
    url = f"{REPLICATE_API}/models/{model_path}/predictions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    body = json.dumps({"input": input_data}).encode()

    result = None
    while result is None:
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            payload = e.read()
            if e.code == 429:
                wait = 11
                try:
                    j = json.loads(payload)
                    if isinstance(j.get("retry_after"), (int, float)):
                        wait = j["retry_after"] + 1
                except Exception:
                    pass
                print(f"    rate-limited, waiting {wait:.0f}s...")
                time.sleep(wait)
                continue
            raise RuntimeError(f"Replicate {e.code}: {payload[:300]!r}")

    poll_req_headers = {"Authorization": f"Bearer {token}"}
    while result.get("status") not in ("succeeded", "failed"):
        time.sleep(2)
        poll = urllib.request.Request(
            f"{REPLICATE_API}/predictions/{result['id']}", headers=poll_req_headers
        )
        with urllib.request.urlopen(poll) as resp:
            result = json.loads(resp.read())

    if result["status"] == "failed":
        raise RuntimeError(f"prediction failed: {result.get('error')}")

    output = result["output"]
    out_url = output[0] if isinstance(output, list) else output
    if not out_url:
        raise RuntimeError("no image URL returned")
    with urllib.request.urlopen(out_url) as resp:
        return resp.read()


def image_data_uri(path: Path) -> str:
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/png;base64,{data}"
