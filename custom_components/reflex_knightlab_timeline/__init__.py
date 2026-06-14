"""reflex-knightlab-timeline.

A native Reflex component that wraps Knight Lab TimelineJS, plus typed Python
builders for its JSON data format.

Typical use::

    import reflex as rx
    from reflex_knightlab_timeline import timeline, TimelineData, Event, Text, TLDate

    data = TimelineData(events=[
        Event(start_date=TLDate(2024, 12, 14), text=Text("My cert", "Description")),
    ])

    def index() -> rx.Component:
        return timeline(data=data, height="600px")
"""

from .models import (
    Background,
    Era,
    Event,
    Media,
    Slide,
    Text,
    TLDate,
    TimelineData,
    load_timeline_data,
)
from .options import TimelineOptions

__version__ = "0.1.0"

__all__ = [
    "TLDate",
    "Text",
    "Media",
    "Background",
    "Slide",
    "Event",
    "Era",
    "TimelineData",
    "TimelineOptions",
    "load_timeline_data",
    "KnightLabTimeline",
    "timeline",
]

# The component depends on Reflex. Keep the data-model layer importable even when
# Reflex is not installed (e.g. for lightweight data tooling or unit tests).
try:
    from .timeline import KnightLabTimeline, timeline
except ModuleNotFoundError:  # pragma: no cover - exercised only without reflex
    KnightLabTimeline = None  # type: ignore[assignment]
    timeline = None  # type: ignore[assignment]
