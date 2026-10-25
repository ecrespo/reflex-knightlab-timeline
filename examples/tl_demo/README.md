# tl_demo — minimal example

A self-contained Reflex app that installs `reflex-knightlab-timeline` **from PyPI**
and renders a timeline built with the typed Python builders, with the TimelineJS
`on_change` event wired into Reflex state.

This example was verified against a clean install of the published `0.2.0` wheel
on Reflex `0.10.0` (Python ≥ 3.11).

## Run

```bash
cd examples/tl_demo
uv venv && uv pip install -r requirements.txt
uv run reflex run
```

Then open http://localhost:3000.
