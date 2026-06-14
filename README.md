# reflex-knightlab-timeline

A native [Reflex](https://reflex.dev/) component that wraps
[Knight Lab **TimelineJS**](https://timeline.knightlab.com/) so you can build
interactive, storytelling timelines in **pure Python** — no HTML, no iframe, no
hand-written JavaScript.

It was built by migrating the certifications timeline from the `reflex_resume`
project (which used an `iframe` → static `timeline.html` → `fetch(timeline.json)`)
into a reusable, reactive, version-pinned component.

```python
import reflex as rx
from reflex_knightlab_timeline import timeline, TimelineData, Event, Text, TLDate

DATA = TimelineData(events=[
    Event(start_date=TLDate(2024, 12, 14),
          text=Text("Claude Code in Action", "Anthropic Academy")),
    Event(start_date=TLDate(2023, 11, 22),
          text=Text("Data Scientist with Python", "Datacamp")),
])

def index() -> rx.Component:
    return timeline(data=DATA, height="600px")

app = rx.App()
app.add_page(index)
```

## Why native instead of an iframe?

| iframe (before) | native component (this package) |
|---|---|
| Isolated from app state | Wired into Reflex state via events (`on_change`, …) |
| Tied to static files/routes | Reusable, `pip install`-able |
| Untyped JSON edited by hand | Typed Python builders + validation |
| Loads TimelineJS from a CDN at runtime | npm `@knight-lab/timelinejs@3.9.11`, reproducible |

## Install

```bash
pip install reflex-knightlab-timeline
# or, from this repo:
pip install -e .
```

Reflex installs the underlying npm package (`@knight-lab/timelinejs@3.9.11`)
automatically on first run.

## Usage

### Data: three ways

```python
from reflex_knightlab_timeline import (
    timeline, TimelineData, Event, Slide, Era, TLDate, Text, Media, Background,
    TimelineOptions, load_timeline_data,
)

# 1) Typed builders
data = TimelineData(
    title=Slide(text=Text("My Journey")),
    events=[Event(start_date=TLDate(2024, 12, 14),
                  text=Text("A cert", "Description"),
                  media=Media(url="https://...", credit="Coursera"))],
    eras=[Era(TLDate(2018), TLDate(2024), Text("Career"))],
    scale="human",
)

# 2) A raw dict (the TimelineJS JSON format)
data = {"events": [{"start_date": {"year": "2024"}, "text": {"headline": "A"}}]}

# 3) Load an existing timeline.json (e.g. migrated from reflex_resume)
data = load_timeline_data("assets/timeline.json")
```

### Options (all TimelineJS options supported)

```python
opts = TimelineOptions(
    timenav_position="bottom",   # "top" | "bottom"
    timenav_height=200,
    scale_factor=2,
    initial_zoom=2,
    hash_bookmark=False,
    default_bg_color={"r": 255, "g": 255, "b": 255},
    language="es",
    theme="dark",                # "dark" | "contrast" | custom CSS url
)
timeline(data=data, options=opts, height="700px")
```

### Events → Python

```python
class State(rx.State):
    current: str = ""

    @rx.event
    def on_slide(self, unique_id: str):
        self.current = unique_id

timeline(data=data, on_change=State.on_slide)
```

Supported events: `on_change`, `on_loaded`, `on_dataloaded`, `on_nav_next`,
`on_nav_previous`, `on_zoom_in`, `on_zoom_out`, `on_back_to_start`.

> TimelineJS needs an explicitly sized container — `width` defaults to `"100%"`
> and `height` to `"600px"`; override as needed.

## Demo

```bash
cd timeline_demo
reflex run
```

The demo renders (1) a timeline authored in Python, and (2) the 178-certification
timeline migrated 1:1 from `reflex_resume`, with live `on_change` updating state.

## Development & tests (TDD)

This package was built test-first. The data layer is pure Python (no Reflex
needed); the component contract tests require Reflex.

```bash
pip install -e ".[dev]"
pytest            # 43 tests
```

## Project layout

```
custom_components/reflex_knightlab_timeline/
  models.py     # typed TimelineJS data builders
  options.py    # all TimelineJS presentation options
  timeline.py   # the native rx.Component (ref + useEffect wrapper)
timeline_demo/  # Reflex demo app (parity with reflex_resume)
tests/          # pytest suite
specs/          # Spec-Driven Design artifacts (PRD, Tech, Data, API, Plan, Migration)
```

See `specs/` for the full design, and `specs/migration/iframe-to-native.md` for
how to swap the old iframe in `reflex_resume`.

## Credits

- [TimelineJS3](https://github.com/NUKnightLab/TimelineJS3) © Northwestern
  University Knight Lab (MPL/own license — see their repo).
- Built on [Reflex](https://reflex.dev/).

## License

MIT — see `LICENSE`.
