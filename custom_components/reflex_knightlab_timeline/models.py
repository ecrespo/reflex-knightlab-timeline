"""Typed builders for Knight Lab TimelineJS data.

This module is pure Python (no Reflex dependency) so it can be unit-tested in
isolation and reused anywhere. Every object exposes ``to_dict()`` which produces
exactly the JSON structure TimelineJS expects, dropping any unset (``None``)
fields. See ``specs/data-model/timeline-schema.md`` for the full contract.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

__all__ = [
    "TLDate",
    "Text",
    "Media",
    "Background",
    "Slide",
    "Event",
    "Era",
    "TimelineData",
    "load_timeline_data",
]

DictLike = "dict[str, Any]"


def _as_dict(value: Any) -> Any:
    """Return ``value.to_dict()`` if it is a builder, else the value itself."""
    if value is None:
        return None
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return value


def _str_or_none(value: Any) -> str | None:
    return None if value is None else str(value)


@dataclass
class TLDate:
    """A TimelineJS date object.

    All components are serialized as strings (a TimelineJS requirement).
    Only ``year`` is mandatory.
    """

    year: Any
    month: Any = None
    day: Any = None
    hour: Any = None
    minute: Any = None
    second: Any = None
    millisecond: Any = None
    display_date: str | None = None
    format: str | None = None

    def __post_init__(self) -> None:
        if self.year is None:
            raise ValueError("TLDate requires a 'year'.")

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key in (
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "second",
            "millisecond",
        ):
            val = _str_or_none(getattr(self, key))
            if val is not None:
                out[key] = val
        if self.display_date is not None:
            out["display_date"] = str(self.display_date)
        if self.format is not None:
            out["format"] = str(self.format)
        return out


@dataclass
class Text:
    """The ``text`` block of a slide: a headline and an HTML body."""

    headline: str | None = None
    text: str | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if self.headline is not None:
            out["headline"] = self.headline
        if self.text is not None:
            out["text"] = self.text
        return out


@dataclass
class Media:
    """The ``media`` block of a slide (image, video, tweet, PDF, etc.)."""

    url: str | None = None
    caption: str | None = None
    credit: str | None = None
    thumbnail: str | None = None
    alt: str | None = None
    title: str | None = None
    link: str | None = None
    link_target: str | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key in (
            "url",
            "caption",
            "credit",
            "thumbnail",
            "alt",
            "title",
            "link",
            "link_target",
        ):
            val = getattr(self, key)
            if val is not None:
                out[key] = val
        return out


@dataclass
class Background:
    """The ``background`` block of a slide (color and/or image url)."""

    url: str | None = None
    color: str | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if self.url is not None:
            out["url"] = self.url
        if self.color is not None:
            out["color"] = self.color
        return out


@dataclass
class Slide:
    """A TimelineJS slide.

    Used both for *events* (which require a ``start_date``) and for the optional
    *title* slide (which does not). ``start_date``/``end_date`` accept a
    :class:`TLDate` or a plain dict; ``text``/``media``/``background`` accept the
    matching builder or a plain dict.
    """

    start_date: TLDate | dict | None = None
    end_date: TLDate | dict | None = None
    text: Text | dict | None = None
    media: Media | dict | None = None
    group: str | None = None
    display_date: str | None = None
    background: Background | dict | None = None
    autolink: bool | None = None
    unique_id: str | None = None

    def validate(self, require_date: bool = True) -> "Slide":
        if require_date:
            sd = _as_dict(self.start_date)
            if not sd or not sd.get("year"):
                raise ValueError(
                    "Event slides must have a 'start_date' with at least a 'year'."
                )
        return self

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if self.start_date is not None:
            out["start_date"] = _as_dict(self.start_date)
        if self.end_date is not None:
            out["end_date"] = _as_dict(self.end_date)
        if self.text is not None:
            out["text"] = _as_dict(self.text)
        if self.media is not None:
            out["media"] = _as_dict(self.media)
        if self.group is not None:
            out["group"] = self.group
        if self.display_date is not None:
            out["display_date"] = self.display_date
        if self.background is not None:
            out["background"] = _as_dict(self.background)
        if self.autolink is not None:
            out["autolink"] = self.autolink
        if self.unique_id is not None:
            out["unique_id"] = self.unique_id
        return out


# An "Event" is just a Slide with a required date. Alias for readability.
Event = Slide


@dataclass
class Era:
    """A labelled span of time shown on the time navigator."""

    start_date: TLDate | dict
    end_date: TLDate | dict
    text: Text | dict | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "start_date": _as_dict(self.start_date),
            "end_date": _as_dict(self.end_date),
        }
        if self.text is not None:
            out["text"] = _as_dict(self.text)
        return out


_VALID_SCALES = {"human", "cosmological"}


@dataclass
class TimelineData:
    """The root TimelineJS data object: ``title``, ``events``, ``eras``, ``scale``."""

    events: list[Slide | dict] = field(default_factory=list)
    title: Slide | dict | None = None
    eras: list[Era | dict] = field(default_factory=list)
    scale: str | None = None

    def add_event(self, **kwargs: Any) -> "TimelineData":
        """Append an :class:`Event` built from keyword arguments."""
        self.events.append(Event(**kwargs))
        return self

    def validate(self) -> "TimelineData":
        if self.scale is not None and self.scale not in _VALID_SCALES:
            raise ValueError(
                f"Invalid scale {self.scale!r}; expected one of {sorted(_VALID_SCALES)}."
            )
        if self.title is not None and hasattr(self.title, "validate"):
            self.title.validate(require_date=False)
        for ev in self.events:
            if hasattr(ev, "validate"):
                ev.validate(require_date=True)
            else:  # plain dict
                if not (ev.get("start_date") or {}).get("year"):
                    raise ValueError("Each event must have a start_date.year.")
        return self

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"events": [_as_dict(e) for e in self.events]}
        if self.title is not None:
            out["title"] = _as_dict(self.title)
        if self.eras:
            out["eras"] = [_as_dict(e) for e in self.eras]
        if self.scale is not None:
            out["scale"] = self.scale
        return out

    # -- parsing -------------------------------------------------------------- #
    @staticmethod
    def _parse_slide(raw: dict[str, Any]) -> Slide:
        def date(d: Any) -> TLDate | None:
            if not d:
                return None
            return TLDate(**d)

        return Slide(
            start_date=date(raw.get("start_date")),
            end_date=date(raw.get("end_date")),
            text=Text(**raw["text"]) if raw.get("text") else None,
            media=Media(**raw["media"]) if raw.get("media") else None,
            group=raw.get("group"),
            display_date=raw.get("display_date"),
            background=Background(**raw["background"]) if raw.get("background") else None,
            autolink=raw.get("autolink"),
            unique_id=raw.get("unique_id"),
        )

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "TimelineData":
        """Parse a TimelineJS JSON dict into a :class:`TimelineData`."""
        eras = []
        for e in raw.get("eras", []) or []:
            eras.append(
                Era(
                    start_date=TLDate(**e["start_date"]),
                    end_date=TLDate(**e["end_date"]),
                    text=Text(**e["text"]) if e.get("text") else None,
                )
            )
        return cls(
            events=[cls._parse_slide(e) for e in raw.get("events", []) or []],
            title=cls._parse_slide(raw["title"]) if raw.get("title") else None,
            eras=eras,
            scale=raw.get("scale"),
        )


def load_timeline_data(path: str | Path, validate: bool = True) -> TimelineData:
    """Load a TimelineJS JSON file into a validated :class:`TimelineData`."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    data = TimelineData.from_dict(raw)
    if validate:
        data.validate()
    return data
