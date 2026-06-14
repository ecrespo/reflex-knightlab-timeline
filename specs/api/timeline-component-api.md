# reflex-knightlab-timeline — Component API Specification

## Metadata

| Campo | Valor |
|---|---|
| **Autor** | Ernesto Crespo |
| **Estado** | `APPROVED` |
| **Versión** | 1.0 (API v1) |
| **Fecha** | 2026-06-14 |
| **PRD Relacionado** | `../prd/timeline-component.md` |
| **Tech Design** | `../technical/timeline-architecture.md` |

> Este "API Spec" describe la **API pública del componente** (props, eventos y
> funciones helper de Python), que es el contrato que consume un desarrollador
> Reflex. No es una API REST.

---

## 1. Punto de Entrada

```python
from reflex_knightlab_timeline import (
    timeline,            # factory del componente (KnightLabTimeline.create)
    KnightLabTimeline,   # la clase del componente
    TimelineData, Slide, Event, Era, TLDate, Text, Media, Background,
    TimelineOptions,
    load_timeline_data,
)
```

## 2. `timeline(...)` / `KnightLabTimeline.create(...)`

Crea el componente.

### Firma

```python
timeline(
    *children,
    data: TimelineData | dict | None = None,
    options: TimelineOptions | dict | None = None,
    validate: bool = False,
    **props,          # width, height, style, class_name, on_change, ...
) -> KnightLabTimeline
```

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `data` | `TimelineData \| dict \| None` | `{"events": []}` | Datos del timeline. Un `TimelineData` se serializa con `.to_dict()`. |
| `options` | `TimelineOptions \| dict \| None` | `{}` | Opciones de presentación (3er arg de `new Timeline`). |
| `validate` | `bool` | `False` | Si `True`, valida `data`/`options` y lanza `ValueError` ante datos inválidos. |
| `width` | `str` | `"100%"` | Ancho del contenedor (requerido por TimelineJS). |
| `height` | `str` | `"600px"` | Alto del contenedor (requerido por TimelineJS). |

### Props del componente

| Prop | Tipo JS | Descripción |
|---|---|---|
| `data` | `object` | Objeto de datos TimelineJS. |
| `options` | `object` | Opciones de presentación. |

## 3. Eventos

Cada evento mapea a `timeline.on(<evento>, cb)` de la API de TimelineJS.

| Prop de evento | Evento TimelineJS | Payload al handler de Python |
|---|---|---|
| `on_change` | `change` | `unique_id: str` del slide actual |
| `on_loaded` | `loaded` | `payload: dict` `{scale, eras, events, title}` |
| `on_dataloaded` | `dataloaded` | — |
| `on_nav_next` | `nav_next` | — |
| `on_nav_previous` | `nav_previous` | — |
| `on_zoom_in` | `zoom_in` | — |
| `on_zoom_out` | `zoom_out` | — |
| `on_back_to_start` | `back_to_start` | — |

### Ejemplo

```python
class State(rx.State):
    current: str = ""

    @rx.event
    def on_slide(self, unique_id: str):
        self.current = unique_id

def page():
    return timeline(data=DATA, on_change=State.on_slide)
```

## 4. `TimelineOptions`

Dataclass con una opción por cada opción documentada de TimelineJS. Solo las
opciones asignadas (no `None`) se emiten; el resto usa el default de TimelineJS.
Un keyword desconocido lanza `TypeError`.

| Grupo | Opciones |
|---|---|
| Tipografía/tema | `font`, `theme`, `language`, `is_embed`, `base_class` |
| Tamaño | `width`, `height`, `default_bg_color` |
| Zoom/escala | `scale_factor`, `initial_zoom`, `zoom_sequence`, `optimal_tick_width`, `duration` |
| Time-nav | `timenav_position`, `timenav_height`, `timenav_height_percentage`, `timenav_mobile_height_percentage`, `timenav_height_min`, `marker_height_min`, `marker_width_min`, `marker_padding`, `menubar_height` |
| Slides/nav | `start_at_slide`, `start_at_end`, `slide_padding_lr`, `slide_default_fade`, `hash_bookmark`, `use_bc`, `dragging`, `track_resize` |
| Integraciones | `script_path`, `soundcite`, `ga_measurement_id`, `debug` |

`TimelineOptions().validate()` lanza `ValueError` si `timenav_position ∉ {"top","bottom"}`.
`track_resize` se emite como `trackResize` (única opción camelCase de TimelineJS).

```python
TimelineOptions(initial_zoom=2, timenav_position="bottom",
                default_bg_color={"r":255,"g":255,"b":255}).to_dict()
# -> {"initial_zoom": 2, "timenav_position": "bottom",
#     "default_bg_color": {"r":255,"g":255,"b":255}}
```

## 5. Builders de Datos

Ver `../data-model/timeline-schema.md` para el contrato completo. Resumen:

```python
TLDate(year, month=None, day=None, hour=None, minute=None, second=None,
       millisecond=None, display_date=None, format=None)
Text(headline=None, text=None)
Media(url=None, caption=None, credit=None, thumbnail=None, alt=None,
      title=None, link=None, link_target=None)
Background(url=None, color=None)
Slide(start_date=None, end_date=None, text=None, media=None, group=None,
      display_date=None, background=None, autolink=None, unique_id=None)
Event = Slide
Era(start_date, end_date, text=None)
TimelineData(events=[], title=None, eras=[], scale=None)
```

Métodos:

| Método | Descripción |
|---|---|
| `<builder>.to_dict()` | Serializa a JSON de TimelineJS (omite `None`). |
| `Slide.validate(require_date=True)` | Valida presencia de `start_date.year`. |
| `TimelineData.validate()` | Valida events + `scale` + title. |
| `TimelineData.add_event(**kwargs)` | Atajo para añadir un `Event`. |
| `TimelineData.from_dict(raw)` | Parsea un dict JSON a builders. |
| `load_timeline_data(path, validate=True)` | Carga y valida un `.json`. |

## 6. Errores

| Situación | Excepción |
|---|---|
| `TLDate` sin `year` | `ValueError` |
| Event sin `start_date.year` (en `validate`) | `ValueError` |
| `scale` inválido | `ValueError` |
| `timenav_position` inválido | `ValueError` |
| Opción desconocida en `TimelineOptions` | `TypeError` |
| (Cliente) clase Timeline no resoluble / init falla | `console.error`, sin crash |

## 7. Compatibilidad

- Python ≥ 3.10, Reflex ≥ 0.8.0, TimelineJS pin `@knight-lab/timelinejs@3.9.11`.
- El componente es SSR-safe (instanciación en cliente).

---

## Historial de Cambios

| Versión | Fecha | Autor | Cambios |
|---|---|---|---|
| 1.0 | 2026-06-14 | Ernesto Crespo | Versión inicial |
