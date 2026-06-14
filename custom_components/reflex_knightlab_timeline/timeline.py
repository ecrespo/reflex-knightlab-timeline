"""Native Reflex wrapper for Knight Lab TimelineJS.

TimelineJS is an *imperative* library: you call ``new Timeline(el, data, options)``
on a DOM node rather than rendering a React element. To make it feel native in
Reflex we ship a tiny React function component (defined as custom code) that owns
a ``div`` ref and, inside ``useEffect``, dynamically imports TimelineJS and
instantiates it on that node. Dynamic import keeps the ``window``/``document``
access out of server-side rendering, and re-running the effect when ``data`` or
``options`` change makes the component reactive to Reflex state.
"""

from __future__ import annotations

from typing import Any

import reflex as rx

from .models import TimelineData
from .options import TimelineOptions

__all__ = ["KnightLabTimeline", "timeline"]

# Pinned npm version researched against the latest release at build time.
TIMELINEJS_VERSION = "3.9.11"
TIMELINEJS_PACKAGE = f"@knight-lab/timelinejs@{TIMELINEJS_VERSION}"

# TimelineJS ships no built ESM/CJS entry point (no main/module/exports field),
# so dynamically importing the package resolves to its *source* `src/js/index.js`,
# whose first line is `import "../less/TL.Timeline.less"`. Vite therefore needs the
# Less preprocessor available at build time. Declaring it here makes bun install it
# into the frontend so the dynamic import compiles cleanly.
LESS_VERSION = "4.6.6"
LESS_PACKAGE = f"less@{LESS_VERSION}"

# The React wrapper injected into the compiled page. It resolves the Timeline
# class across CJS/ESM interop shapes, instantiates it, and wires the event API
# (timeline.on(...)) back to the Reflex event handlers passed as props.
_WRAPPER_JS = """
function KnightLabTimeline({ data, options, onChange, onLoaded, onDataloaded,
                            onNavNext, onNavPrevious, onZoomIn, onZoomOut,
                            onBackToStart, ...rest }) {
  const containerRef = useRef(null);
  const timelineRef = useRef(null);
  useEffect(() => {
    let active = true;
    const el = containerRef.current;
    if (!el) return;
    el.innerHTML = "";
    import("@knight-lab/timelinejs").then((mod) => {
      if (!active || !containerRef.current) return;
      const TimelineClass =
        (mod && mod.Timeline) ||
        (mod && mod.default && mod.default.Timeline) ||
        (mod && mod.default) ||
        (typeof TL !== "undefined" ? TL.Timeline : undefined);
      if (!TimelineClass) {
        console.error("[reflex-knightlab-timeline] Could not resolve Timeline class");
        return;
      }
      let tl;
      try {
        tl = new TimelineClass(containerRef.current, data, options || {});
      } catch (err) {
        console.error("[reflex-knightlab-timeline] init error:", err);
        return;
      }
      timelineRef.current = tl;
      if (tl && typeof tl.on === "function") {
        if (onChange) tl.on("change", (d) => onChange((d && d.unique_id) || ""));
        if (onLoaded) tl.on("loaded", (d) => onLoaded(d || {}));
        if (onDataloaded) tl.on("dataloaded", () => onDataloaded());
        if (onNavNext) tl.on("nav_next", () => onNavNext());
        if (onNavPrevious) tl.on("nav_previous", () => onNavPrevious());
        if (onZoomIn) tl.on("zoom_in", () => onZoomIn());
        if (onZoomOut) tl.on("zoom_out", () => onZoomOut());
        if (onBackToStart) tl.on("back_to_start", () => onBackToStart());
      }
    }).catch((err) =>
      console.error("[reflex-knightlab-timeline] load error:", err)
    );
    return () => {
      active = false;
      timelineRef.current = null;
      if (el) el.innerHTML = "";
    };
  }, [JSON.stringify(data), JSON.stringify(options)]);
  return <div ref={containerRef} {...rest} />;
}
""".strip()


class KnightLabTimeline(rx.Component):
    """An interactive Knight Lab TimelineJS timeline, native to Reflex."""

    # Rendered from the custom-code wrapper above (no named npm import for the
    # tag itself, which would fail because TimelineJS exports a class, not a
    # React component).
    tag = "KnightLabTimeline"

    # Ensure the npm package is installed and version-pinned. `less` is required
    # so Vite can compile the `.less` that TimelineJS' source entry imports.
    lib_dependencies: list[str] = [TIMELINEJS_PACKAGE, LESS_PACKAGE]

    # The TimelineJS data object (title / events / eras / scale).
    data: rx.Var[dict]

    # Presentation options (third argument of new TL.Timeline(...)).
    options: rx.Var[dict]

    # ---- Event triggers mapping to the TimelineJS event API ---------------- #
    on_change: rx.EventHandler[lambda unique_id: [unique_id]]
    on_loaded: rx.EventHandler[lambda payload: [payload]]
    on_dataloaded: rx.EventHandler[lambda: []]
    on_nav_next: rx.EventHandler[lambda: []]
    on_nav_previous: rx.EventHandler[lambda: []]
    on_zoom_in: rx.EventHandler[lambda: []]
    on_zoom_out: rx.EventHandler[lambda: []]
    on_back_to_start: rx.EventHandler[lambda: []]

    def add_imports(self) -> dict[str, Any]:
        return {
            "react": ["useRef", "useEffect"],
            # CSS side-effect import; also pulls the npm package into package.json.
            "": ["@knight-lab/timelinejs/dist/css/timeline.css"],
        }

    def add_custom_code(self) -> list[str]:
        return [_WRAPPER_JS]

    @classmethod
    def create(  # type: ignore[override]
        cls,
        *children: Any,
        data: TimelineData | dict | None = None,
        options: TimelineOptions | dict | None = None,
        validate: bool = False,
        **props: Any,
    ) -> "KnightLabTimeline":
        """Create a timeline.

        Args:
            data: A :class:`TimelineData` or a raw TimelineJS dict.
            options: A :class:`TimelineOptions` or a raw options dict.
            validate: If True, validate ``data``/``options`` before rendering.
            **props: Standard Reflex props (style, width, height, event handlers).
        """
        if isinstance(data, TimelineData):
            if validate:
                data.validate()
            data = data.to_dict()
        elif data is None:
            data = {"events": []}

        if isinstance(options, TimelineOptions):
            if validate:
                options.validate()
            options = options.to_dict()
        elif options is None:
            options = {}

        # TimelineJS requires an explicitly sized container.
        props.setdefault("width", "100%")
        props.setdefault("height", "600px")

        return super().create(*children, data=data, options=options, **props)


# Convenience alias matching the Reflex `rx.<component>` calling style.
timeline = KnightLabTimeline.create
