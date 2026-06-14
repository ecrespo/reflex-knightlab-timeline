"""TDD: contract for the TimelineJS data model builders.

These tests define how Python objects must serialize to the JSON that
Knight Lab TimelineJS expects (see specs/data-model/timeline-schema.md).
They are pure-Python and do not require Reflex to be installed.
"""

import json

import pytest

from reflex_knightlab_timeline.models import (
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


# --------------------------------------------------------------------------- #
# TLDate
# --------------------------------------------------------------------------- #
class TestTLDate:
    def test_year_only(self):
        assert TLDate(2024).to_dict() == {"year": "2024"}

    def test_full_date_is_stringified(self):
        d = TLDate(year=2024, month=12, day=14).to_dict()
        assert d == {"year": "2024", "month": "12", "day": "14"}
        # every value must be a string (TimelineJS requirement)
        assert all(isinstance(v, str) for v in d.values())

    def test_none_fields_are_dropped(self):
        d = TLDate(year="2024", day="5").to_dict()
        assert "month" not in d
        assert d == {"year": "2024", "day": "5"}

    def test_display_date_and_format(self):
        d = TLDate(2024, display_date="Spring 2024", format="yyyy").to_dict()
        assert d["display_date"] == "Spring 2024"
        assert d["format"] == "yyyy"

    def test_year_is_required(self):
        with pytest.raises((TypeError, ValueError)):
            TLDate()  # type: ignore[call-arg]


# --------------------------------------------------------------------------- #
# Text / Media / Background
# --------------------------------------------------------------------------- #
class TestSimpleValueObjects:
    def test_text(self):
        assert Text("Headline", "Body").to_dict() == {
            "headline": "Headline",
            "text": "Body",
        }

    def test_text_drops_none(self):
        assert Text(headline="Only headline").to_dict() == {"headline": "Only headline"}

    def test_media_full(self):
        m = Media(
            url="https://x/cert.pdf",
            credit="Coursera",
            caption="My cert",
            thumbnail="https://x/t.png",
            alt="alt text",
            title="title",
            link="https://x",
            link_target="_blank",
        ).to_dict()
        assert m["url"] == "https://x/cert.pdf"
        assert m["credit"] == "Coursera"
        assert m["link_target"] == "_blank"

    def test_media_drops_none(self):
        assert Media(url="u").to_dict() == {"url": "u"}

    def test_background(self):
        assert Background(color="#f5f5dc").to_dict() == {"color": "#f5f5dc"}


# --------------------------------------------------------------------------- #
# Slide / Event
# --------------------------------------------------------------------------- #
class TestSlide:
    def test_event_is_alias_of_slide(self):
        assert Event is Slide

    def test_minimal_event_serialization(self):
        ev = Event(
            start_date=TLDate(2024, 12, 14),
            text=Text("Cert", "Desc"),
            media=Media(url="u", credit="Coursera"),
        )
        d = ev.to_dict()
        assert d["start_date"] == {"year": "2024", "month": "12", "day": "14"}
        assert d["text"] == {"headline": "Cert", "text": "Desc"}
        assert d["media"] == {"url": "u", "credit": "Coursera"}

    def test_accepts_plain_dicts_too(self):
        ev = Event(start_date={"year": "2024"}, text={"headline": "H"})
        d = ev.to_dict()
        assert d["start_date"] == {"year": "2024"}
        assert d["text"] == {"headline": "H"}

    def test_optional_fields(self):
        ev = Event(
            start_date=TLDate(2024),
            end_date=TLDate(2025),
            group="Certs",
            display_date="2024",
            background=Background(color="#000"),
            unique_id="cert-1",
            autolink=False,
        )
        d = ev.to_dict()
        assert d["end_date"] == {"year": "2025"}
        assert d["group"] == "Certs"
        assert d["display_date"] == "2024"
        assert d["background"] == {"color": "#000"}
        assert d["unique_id"] == "cert-1"
        assert d["autolink"] is False

    def test_event_validation_requires_year(self):
        with pytest.raises(ValueError):
            Event(text=Text("no date")).validate(require_date=True)

    def test_title_slide_does_not_require_date(self):
        # title slides are allowed to omit a start_date
        Slide(text=Text("My Title")).validate(require_date=False)


# --------------------------------------------------------------------------- #
# Era
# --------------------------------------------------------------------------- #
class TestEra:
    def test_era_serialization(self):
        era = Era(
            start_date=TLDate(2018),
            end_date=TLDate(2024),
            text=Text("Career era"),
        )
        d = era.to_dict()
        assert d["start_date"] == {"year": "2018"}
        assert d["end_date"] == {"year": "2024"}
        assert d["text"] == {"headline": "Career era"}


# --------------------------------------------------------------------------- #
# TimelineData
# --------------------------------------------------------------------------- #
class TestTimelineData:
    def test_events_only(self):
        data = TimelineData(events=[Event(start_date=TLDate(2024), text=Text("A"))])
        d = data.to_dict()
        assert "events" in d and len(d["events"]) == 1
        assert "title" not in d  # absent when not provided

    def test_full_structure(self):
        data = TimelineData(
            title=Slide(text=Text("Title")),
            events=[Event(start_date=TLDate(2024), text=Text("A"))],
            eras=[Era(TLDate(2020), TLDate(2024), Text("Era"))],
            scale="human",
        )
        d = data.to_dict()
        assert d["title"]["text"]["headline"] == "Title"
        assert d["scale"] == "human"
        assert len(d["eras"]) == 1

    def test_is_json_serializable(self):
        data = TimelineData(events=[Event(start_date=TLDate(2024), text=Text("A"))])
        # must round-trip through json without errors
        s = json.dumps(data.to_dict())
        assert json.loads(s)["events"][0]["start_date"]["year"] == "2024"

    def test_validate_rejects_event_without_year(self):
        data = TimelineData(events=[Event(text=Text("no date"))])
        with pytest.raises(ValueError):
            data.validate()

    def test_validate_rejects_bad_scale(self):
        data = TimelineData(
            events=[Event(start_date=TLDate(2024))], scale="galactic"
        )
        with pytest.raises(ValueError):
            data.validate()

    def test_add_event_helper(self):
        data = TimelineData()
        data.add_event(start_date=TLDate(2024), text=Text("A"))
        assert len(data.to_dict()["events"]) == 1

    def test_from_dict_roundtrip(self):
        raw = {
            "events": [
                {
                    "start_date": {"year": "2024", "month": "12", "day": "14"},
                    "media": {"url": "u", "credit": "Coursera"},
                    "text": {"headline": "Cert", "text": "Cert"},
                }
            ]
        }
        data = TimelineData.from_dict(raw)
        assert data.to_dict() == raw


# --------------------------------------------------------------------------- #
# load_timeline_data
# --------------------------------------------------------------------------- #
class TestLoadTimelineData:
    def test_loads_and_validates_json_file(self, tmp_path):
        raw = {
            "events": [
                {
                    "start_date": {"year": "2024"},
                    "text": {"headline": "Cert"},
                }
            ]
        }
        p = tmp_path / "timeline.json"
        p.write_text(json.dumps(raw), encoding="utf-8")
        data = load_timeline_data(p)
        assert isinstance(data, TimelineData)
        assert data.to_dict()["events"][0]["start_date"]["year"] == "2024"
