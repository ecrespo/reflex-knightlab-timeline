"""Demo app for reflex-knightlab-timeline.

Shows three things:

1. A timeline built entirely from the typed Python builders.
2. A timeline migrated 1:1 from the original ``reflex_resume`` certifications
   ``timeline.json`` (parity with the old iframe embed), loaded at import time.
3. Live interactivity: the ``on_change`` event updates Reflex state, proving the
   imperative TimelineJS event API is wired into Python — something the old
   iframe approach could not do.
"""

from pathlib import Path

import reflex as rx

from reflex_knightlab_timeline import (
    Event,
    Media,
    Slide,
    Text,
    TimelineData,
    TimelineOptions,
    TLDate,
    load_timeline_data,
    timeline,
)

ASSETS = Path(__file__).resolve().parent.parent / "assets"

# 1) A timeline authored in pure Python -------------------------------------- #
PYTHON_TIMELINE = TimelineData(
    title=Slide(
        text=Text("My Learning Journey", "Built with reflex-knightlab-timeline")
    ),
    events=[
        Event(
            start_date=TLDate(2024, 12, 14),
            text=Text("Claude Code in Action", "Anthropic Academy"),
            media=Media(credit="Anthropic Academy"),
            group="AI",
        ),
        Event(
            start_date=TLDate(2025, 12, 9),
            text=Text("Building Autonomous AI Agents", "LangGraph"),
            group="AI",
        ),
        Event(
            start_date=TLDate(2023, 11, 22),
            text=Text("Data Scientist Professional with Python", "Datacamp"),
            media=Media(credit="Datacamp"),
            group="Data",
        ),
    ],
    scale="human",
).validate()

# 2) Parity timeline migrated from reflex_resume/assets/timeline.json --------- #
RESUME_TIMELINE = load_timeline_data(ASSETS / "timeline.json")

OPTIONS = TimelineOptions(
    timenav_height=200,
    scale_factor=2,
    initial_zoom=2,
    hash_bookmark=False,
    default_bg_color={"r": 255, "g": 255, "b": 255},
    timenav_position="bottom",
).validate()


class State(rx.State):
    """Captures TimelineJS events on the Python side."""

    current_slide: str = "(navigate the timeline)"

    @rx.event
    def on_slide_change(self, unique_id: str):
        self.current_slide = f"Current slide id: {unique_id or '—'}"


def section(title: str, *children: rx.Component) -> rx.Component:
    return rx.box(
        rx.heading(title, size="5", margin_bottom="0.5rem"),
        *children,
        margin_bottom="2.5rem",
    )


def index() -> rx.Component:
    return rx.container(
        rx.heading("reflex-knightlab-timeline", size="8", margin_y="1rem"),
        rx.text(
            "A native Reflex wrapper for Knight Lab TimelineJS.",
            color_scheme="gray",
            margin_bottom="2rem",
        ),
        section(
            "1 · Authored in pure Python",
            timeline(
                data=PYTHON_TIMELINE,
                options=OPTIONS,
                on_change=State.on_slide_change,
                height="500px",
            ),
            rx.callout(State.current_slide, margin_top="0.75rem"),
        ),
        section(
            "2 · Migrated from reflex_resume (parity, 178 certifications)",
            timeline(data=RESUME_TIMELINE, options=OPTIONS, height="600px"),
        ),
        max_width="1100px",
    )


app = rx.App()
app.add_page(index, title="reflex-knightlab-timeline demo")
