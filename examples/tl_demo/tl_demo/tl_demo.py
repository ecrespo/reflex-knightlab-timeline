"""Sandbox demo for the PyPI-published reflex-knightlab-timeline package.

Proves a clean install integrates into a real Reflex app: typed Python builders,
presentation options, and the imperative TimelineJS `on_change` event wired back
into Reflex state.
"""

import reflex as rx

from reflex_knightlab_timeline import (
    Event,
    Media,
    Slide,
    Text,
    TLDate,
    TimelineData,
    TimelineOptions,
    timeline,
)

# --- Timeline content authored entirely in typed Python ---------------------- #
DATA = TimelineData(
    title=Slide(text=Text("reflex-knightlab-timeline", "A native Reflex component")),
    events=[
        Event(
            start_date=TLDate(2024, 12, 14),
            text=Text("Claude Code in Action", "Anthropic Academy"),
            media=Media(url="https://reflex.dev/", credit="Reflex"),
        ),
        Event(
            start_date=TLDate(2023, 11, 22),
            text=Text("Data Scientist with Python", "Datacamp"),
        ),
        Event(
            start_date=TLDate(2022, 6, 1),
            text=Text("Started the journey", "First milestone"),
        ),
    ],
    scale="human",
)

OPTIONS = TimelineOptions(
    timenav_position="bottom",
    hash_bookmark=False,
    initial_zoom=2,
)


class State(rx.State):
    """Holds the unique_id of the slide TimelineJS is currently showing."""

    current_slide: str = ""

    @rx.event
    def on_slide_change(self, unique_id: str):
        self.current_slide = unique_id


def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("reflex-knightlab-timeline — sandbox demo", size="6"),
            rx.text("Clean install from PyPI (v0.1.2)."),
            rx.text(
                "Current slide: ",
                rx.code(rx.cond(State.current_slide != "", State.current_slide, "—")),
            ),
            timeline(
                data=DATA,
                options=OPTIONS,
                on_change=State.on_slide_change,
                height="600px",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        max_width="1100px",
        padding="4",
    )


app = rx.App()
app.add_page(index, route="/")
