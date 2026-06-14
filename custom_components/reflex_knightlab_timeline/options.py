"""Typed presentation options for TimelineJS.

One field per documented option
(https://timeline.knightlab.com/docs/options.html). Unset options are omitted
from ``to_dict()`` so TimelineJS falls back to its own defaults. Passing an
unknown keyword raises ``TypeError`` (dataclass behaviour), which catches typos
early.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = ["TimelineOptions"]

_VALID_TIMENAV_POSITIONS = {"top", "bottom"}

# Most TimelineJS options are snake_case, but a few are camelCase in the JS API.
_KEY_MAP = {"track_resize": "trackResize"}


@dataclass
class TimelineOptions:
    """A subset-friendly wrapper over the full TimelineJS options object."""

    # Presentation / typography
    font: str | None = None
    theme: str | None = None  # "dark", "contrast", or a CSS url
    language: str | None = None
    is_embed: bool | None = None
    base_class: str | None = None

    # Sizing
    width: Any = None
    height: Any = None
    default_bg_color: Any = None  # hex string, css name, or {r,g,b}

    # Zoom / scale
    scale_factor: Any = None
    initial_zoom: int | None = None
    zoom_sequence: list[Any] | None = None
    optimal_tick_width: int | None = None
    duration: int | None = None

    # Time navigator
    timenav_position: str | None = None
    timenav_height: int | None = None
    timenav_height_percentage: int | None = None
    timenav_mobile_height_percentage: int | None = None
    timenav_height_min: int | None = None
    marker_height_min: int | None = None
    marker_width_min: int | None = None
    marker_padding: int | None = None
    menubar_height: int | None = None

    # Slides / navigation
    start_at_slide: int | None = None
    start_at_end: bool | None = None
    slide_padding_lr: int | None = None
    slide_default_fade: str | None = None
    hash_bookmark: bool | None = None
    use_bc: bool | None = None
    dragging: bool | None = None
    track_resize: bool | None = None

    # Integrations / misc
    script_path: str | None = None
    soundcite: bool | None = None
    ga_measurement_id: str | None = None
    debug: bool | None = None

    def validate(self) -> "TimelineOptions":
        if (
            self.timenav_position is not None
            and self.timenav_position not in _VALID_TIMENAV_POSITIONS
        ):
            raise ValueError(
                f"timenav_position must be one of {sorted(_VALID_TIMENAV_POSITIONS)}; "
                f"got {self.timenav_position!r}."
            )
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            _KEY_MAP.get(k, k): v
            for k, v in self.__dict__.items()
            if v is not None
        }
