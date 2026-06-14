"""TDD: contract for the TimelineOptions presentation config object.

Mirrors the documented TimelineJS options
(https://timeline.knightlab.com/docs/options.html).
"""

import json

import pytest

from reflex_knightlab_timeline.options import TimelineOptions


class TestTimelineOptions:
    def test_empty_options_is_empty_dict(self):
        assert TimelineOptions().to_dict() == {}

    def test_only_set_options_are_emitted(self):
        opts = TimelineOptions(initial_zoom=2, hash_bookmark=False)
        d = opts.to_dict()
        assert d == {"initial_zoom": 2, "hash_bookmark": False}

    def test_parity_options_from_legacy_iframe(self):
        # the exact options used by the original reflex_resume timeline.html
        opts = TimelineOptions(
            timenav_height=200,
            timenav_height_percentage=25,
            scale_factor=2,
            initial_zoom=2,
            hash_bookmark=False,
            default_bg_color={"r": 255, "g": 255, "b": 255},
            timenav_position="bottom",
        )
        d = opts.to_dict()
        assert d["timenav_height"] == 200
        assert d["default_bg_color"] == {"r": 255, "g": 255, "b": 255}
        assert d["timenav_position"] == "bottom"

    def test_supports_advanced_options(self):
        opts = TimelineOptions(
            font="opensans-gentiumbook",
            language="es",
            start_at_end=True,
            theme="dark",
            timenav_position="top",
        )
        d = opts.to_dict()
        assert d["font"] == "opensans-gentiumbook"
        assert d["language"] == "es"
        assert d["start_at_end"] is True

    def test_default_bg_color_accepts_hex_string(self):
        assert TimelineOptions(default_bg_color="#ffffff").to_dict()[
            "default_bg_color"
        ] == "#ffffff"

    def test_is_json_serializable(self):
        opts = TimelineOptions(initial_zoom=3, zoom_sequence=[1, 2, 3, 5, 8])
        s = json.dumps(opts.to_dict())
        assert json.loads(s)["zoom_sequence"] == [1, 2, 3, 5, 8]

    def test_rejects_unknown_option(self):
        with pytest.raises(TypeError):
            TimelineOptions(not_a_real_option=True)  # type: ignore[call-arg]

    def test_validate_rejects_bad_timenav_position(self):
        with pytest.raises(ValueError):
            TimelineOptions(timenav_position="sideways").validate()
