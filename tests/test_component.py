"""TDD: contract for the native Reflex component wrapper.

These tests require Reflex to be installed; if it is not present they are
skipped (the pure data-model tests still cover the serialization layer).
"""

import pytest

reflex = pytest.importorskip("reflex")

from reflex_knightlab_timeline.models import Event, Text, TimelineData, TLDate
from reflex_knightlab_timeline.options import TimelineOptions
from reflex_knightlab_timeline.timeline import KnightLabTimeline, timeline


@pytest.fixture
def sample_data():
    return TimelineData(
        events=[Event(start_date=TLDate(2024, 12, 14), text=Text("Cert", "Desc"))]
    )


class TestComponentContract:
    def test_tag_is_locally_defined(self):
        # rendered as a custom-code React component, no bad named npm import
        assert KnightLabTimeline.tag == "KnightLabTimeline"

    def test_declares_timelinejs_dependency(self):
        deps = KnightLabTimeline().lib_dependencies
        assert any("@knight-lab/timelinejs" in d for d in deps)

    def test_imports_css_and_react_hooks(self):
        imports = KnightLabTimeline().add_imports()
        # CSS side-effect import (empty key) pulls the npm package + styles
        css_imports = imports.get("", [])
        if isinstance(css_imports, str):
            css_imports = [css_imports]
        assert any("timeline.css" in c for c in css_imports)
        assert "useRef" in imports.get("react", [])
        assert "useEffect" in imports.get("react", [])

    def test_custom_code_defines_wrapper_and_instantiates_timeline(self):
        code = "\n".join(KnightLabTimeline().add_custom_code())
        assert "function KnightLabTimeline" in code
        assert "useEffect" in code
        assert "useRef" in code
        # instantiates the imperative TimelineJS class on the div ref
        assert "new " in code and "Timeline" in code
        assert "@knight-lab/timelinejs" in code

    def test_event_triggers_exist(self):
        triggers = KnightLabTimeline.get_event_triggers()
        for ev in [
            "on_change",
            "on_loaded",
            "on_nav_next",
            "on_nav_previous",
            "on_zoom_in",
            "on_zoom_out",
        ]:
            assert ev in triggers


class TestComponentCreation:
    def test_create_accepts_timeline_data_object(self, sample_data):
        comp = KnightLabTimeline.create(data=sample_data)
        # the data prop must be serialized to a plain dict for the JS side
        rendered = str(comp)
        assert "2024" in rendered

    def test_create_accepts_options_object(self, sample_data):
        comp = KnightLabTimeline.create(
            data=sample_data, options=TimelineOptions(initial_zoom=2)
        )
        assert comp is not None

    def test_create_sets_default_dimensions(self, sample_data):
        comp = KnightLabTimeline.create(data=sample_data)
        style = comp.style or {}
        # TimelineJS needs an explicitly sized container
        assert ("width" in style) or (getattr(comp, "width", None) is not None)

    def test_helper_alias_creates_component(self, sample_data):
        comp = timeline(data=sample_data)
        assert isinstance(comp, KnightLabTimeline)

    def test_data_validation_runs_on_create(self):
        bad = TimelineData(events=[Event(text=Text("no date"))])
        with pytest.raises(ValueError):
            KnightLabTimeline.create(data=bad, validate=True)
