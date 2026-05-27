#!/usr/bin/env python3
"""DailyCuriosity MVP: topic -> production-ready short-form video script.

The smallest end-to-end slice of the content pipeline. Give it a topic and it
returns a voiceover-ready script (hook, beat-by-beat narration with on-screen
text and b-roll directions, CTA, caption, hashtags) using Claude.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python generate_script.py "Perche' dimentichiamo i sogni appena svegli"
    python generate_script.py "The Mandela Effect" --lang en --duration 60

Output is printed and saved as Markdown under ./output/.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime, timezone

import anthropic

MODEL = "claude-opus-4-7"

# Stable across every run -> sits first in the prompt so it can be cached.
# Keep volatile, per-request details (the topic, language, duration) out of
# here; they go in the user message after the cached prefix.
SYSTEM_PROMPT = """\
You are the head scriptwriter for "DailyCuriosity", a viral short-form video \
channel (TikTok / Reels / YouTube Shorts). The channel sits at the intersection \
of curiosity, psychology, mysteries, science, and human behavior.

Your job: turn a single topic into a complete, production-ready script that a \
solo creator can shoot and edit the same day.

Non-negotiable quality bar:
- HOOK in the first 2 seconds. Open on tension, a bold claim, a question, or a \
pattern interrupt. Never open with "Did you know" or a slow intro.
- RETENTION: every 3-5 seconds give a new beat, reveal, or visual change. No \
filler. Each line must earn the next one.
- PAYOFF: deliver a satisfying, concrete answer or twist. Do not bait without \
paying off.
- The narration must be voiceover-ready: short, spoken-rhythm sentences a \
person can read aloud naturally.
- Be accurate. If a claim is contested or a myth, frame it honestly.

Output format (Markdown, in this exact structure):

# <punchy title>

**Alt titles:** three alternative title/hook options, one per line.

## Hook (0-2s)
<the spoken hook>

## Script
A table or beat list. For each beat give:
- **Time** (e.g. 0-3s)
- **Voiceover** — what is said
- **On-screen text** — the caption/keyword overlay
- **B-roll / Visual** — concrete shot or stock-footage direction

## CTA
<the call to action: follow / comment prompt / save>

## Caption
<the post caption, scroll-stopping first line>

## Hashtags
<8-12 relevant hashtags on one line>

## Production notes
<pacing, music vibe, cut rhythm, total runtime>

Write the title, narration, on-screen text, caption, and hashtags in the target \
language given by the user. Keep production directions (B-roll, notes) in the \
same language. Aim the total runtime at the requested duration.
"""


def build_user_prompt(topic: str, lang: str, duration: int, niche: str) -> str:
    return (
        f"Topic: {topic}\n"
        f"Target language: {lang}\n"
        f"Target duration: {duration} seconds\n"
        f"Angle / niche emphasis: {niche}\n\n"
        "Write the full script now."
    )


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:60] or "script"


def generate(topic: str, lang: str, duration: int, niche: str) -> tuple[str, anthropic.types.Usage]:
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the env
    response = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        # effort: medium is a good cost/quality balance for creative drafting.
        output_config={"effort": "medium"},
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                # Caches the stable prefix so repeated runs reuse it. Kicks in
                # once the prefix exceeds the model's minimum cacheable size.
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {"role": "user", "content": build_user_prompt(topic, lang, duration, niche)}
        ],
    )
    script = "".join(block.text for block in response.content if block.type == "text")
    return script, response.usage


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a production-ready short-form video script from a topic."
    )
    parser.add_argument("topic", help="The subject of the video.")
    parser.add_argument("--lang", default="it", help="Target language (default: it).")
    parser.add_argument(
        "--duration", type=int, default=45, help="Target runtime in seconds (default: 45)."
    )
    parser.add_argument(
        "--niche",
        default="curiosity, psychology, mysteries, science, human behavior",
        help="Niche emphasis to steer the angle.",
    )
    parser.add_argument("--out", default="output", help="Output directory (default: output).")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: set ANTHROPIC_API_KEY before running.", file=sys.stderr)
        return 1

    try:
        script, usage = generate(args.topic, args.lang, args.duration, args.niche)
    except anthropic.APIError as exc:
        print(f"API error: {exc}", file=sys.stderr)
        return 1

    os.makedirs(args.out, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = os.path.join(args.out, f"{stamp}-{slugify(args.topic)}.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(script)

    print(script)
    print(f"\n---\nSaved: {path}")
    cached = usage.cache_read_input_tokens or 0
    print(
        f"Tokens: in={usage.input_tokens} cached={cached} out={usage.output_tokens}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
