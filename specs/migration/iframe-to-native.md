# Migración: iframe estático → componente Reflex nativo

## Metadata

| Campo | Valor |
|---|---|
| **Autor** | Ernesto Crespo |
| **Estado** | `APPROVED` |
| **Versión** | 1.0 |
| **Fecha** | 2026-06-14 |

---

## 1. Antes (en `reflex_resume`)

**`web/components/resume_sections.py`**

```python
def certifications_section() -> rx.Component:
    return rx.el.section(
        section_heading("Certifications"),
        rx.el.iframe(
            src="/timeline.html",
            class_name="w-full border-0 rounded-lg shadow-md h-[400px] md:h-[700px] lg:h-[800px]",
            style={"background": "white"},
        ),
        id="certifications",
        class_name="mb-12 scroll-mt-24",
    )
```

**`assets/timeline.html`** (estático) cargaba TimelineJS desde el CDN, hacía
`fetch('/timeline.json')` e instanciaba `new TL.Timeline('timeline-embed', data, {...})`.

### Limitaciones del enfoque iframe

1. **Aislamiento:** el timeline vive en otro documento; no hay puente con el estado de Reflex.
2. **No reutilizable:** atado a rutas estáticas (`/timeline.html`, `/timeline.json`).
3. **Sin tipado/validación** de los datos.
4. **Dependencia de CDN** en tiempo de ejecución.

## 2. Después (con `reflex-knightlab-timeline`)

```python
import reflex as rx
from reflex_knightlab_timeline import timeline, load_timeline_data, TimelineOptions

CERTS = load_timeline_data("assets/timeline.json")  # mismos 178 eventos
OPTS = TimelineOptions(
    timenav_height=200, scale_factor=2, initial_zoom=2,
    hash_bookmark=False, default_bg_color={"r":255,"g":255,"b":255},
    timenav_position="bottom",
)

def certifications_section() -> rx.Component:
    return rx.el.section(
        section_heading("Certifications"),
        timeline(
            data=CERTS,
            options=OPTS,
            width="100%",
            height="800px",
            class_name="border-0 rounded-lg shadow-md",
        ),
        id="certifications",
        class_name="mb-12 scroll-mt-24",
    )
```

## 3. Mapeo de equivalencias

| Antes (iframe/HTML/JSON) | Después (componente) |
|---|---|
| `<iframe src="/timeline.html">` | `timeline(...)` (mismo documento, React) |
| `<link>`/`<script>` del CDN | npm `@knight-lab/timelinejs@3.9.11` (instalado por Reflex) |
| `fetch('/timeline.json')` | `load_timeline_data("timeline.json")` o `data=TimelineData(...)` |
| Objeto `options` JS inline | `TimelineOptions(...)` tipado |
| (no había) | Eventos: `on_change`, `on_nav_next`, … → estado Python |
| `h-[400px] md:h-[700px]` | `height="800px"` o `style`/`class_name` Reflex |

### Paridad de opciones

Las opciones del `timeline.html` original se mapean 1:1:

```
timenav_height: 200            → TimelineOptions(timenav_height=200)
timenav_height_percentage: 25  → timenav_height_percentage=25
scale_factor: 2                → scale_factor=2
initial_zoom: 2                → initial_zoom=2
hash_bookmark: false           → hash_bookmark=False
default_bg_color: {255,255,255}→ default_bg_color={"r":255,"g":255,"b":255}
timenav_position: "bottom"     → timenav_position="bottom"
```

## 4. Pasos de migración para `reflex_resume` (opcional)

1. `pip install reflex-knightlab-timeline` (o instalar desde el repo local).
2. Reemplazar `certifications_section()` por la versión "Después".
3. Eliminar (opcional) `assets/timeline.html`; mantener `assets/timeline.json` como fuente de datos.
4. `reflex run` y verificar paridad visual + que las certificaciones aparecen.

> La migración del consumidor es **opcional** y no rompe nada: el `timeline.json`
> sigue siendo el mismo formato. Este repo entrega el componente; adoptarlo en
> `reflex_resume` es un cambio aislado de una función.

## 5. Mejoras obtenidas con la migración

- **Reactividad:** `on_change` (y demás) actualizan el estado de Reflex.
- **Reutilización:** instalable en cualquier proyecto Reflex.
- **Tipado y validación:** errores de datos detectados en Python, no en runtime del navegador.
- **Sin dependencia de CDN** en ejecución; versión de TimelineJS fijada y reproducible.
- **SSR-safe** por diseño.
