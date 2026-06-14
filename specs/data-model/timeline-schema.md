# TimelineJS Data — Data Model Specification

## Metadata

| Campo | Valor |
|---|---|
| **Autor** | Ernesto Crespo |
| **Estado** | `APPROVED` |
| **Versión** | 1.0 |
| **Fecha** | 2026-06-14 |
| **Formato** | JSON (TimelineJS 3.9.x) |
| **Tech Design Relacionado** | `../technical/timeline-architecture.md` |

---

## 1. Visión General del Modelo

TimelineJS consume un único objeto JSON raíz con: un `title` opcional (un slide), un array `events` (slides con fecha), un array `eras` opcional (franjas de tiempo) y un `scale` opcional. Este spec define cómo los builders de Python (`models.py`) mapean 1:1 a ese JSON.

### Diagrama de Relaciones (composición)

```
TimelineData
├── title:  Slide?            (sin fecha obligatoria)
├── events: [Slide]           (cada uno requiere start_date.year)
│     ├── start_date: TLDate  (requerido)
│     ├── end_date:   TLDate? 
│     ├── text:       Text?    {headline, text}
│     ├── media:      Media?   {url, credit, caption, thumbnail, ...}
│     └── background: Background? {url, color}
├── eras:   [Era]             {start_date, end_date, text}
└── scale:  "human" | "cosmological"?
```

## 2. Entidades

### 2.1 `TLDate`

**Propósito:** fecha de TimelineJS. **Regla clave:** todos los componentes se serializan como **string**; solo `year` es obligatorio.

#### Campos

| Campo | Tipo entrada | Requerido | Serializa como | Notas |
|---|---|---|---|---|
| `year` | int/str | Sí | `"year"` string | Único obligatorio |
| `month` | int/str | No | `"month"` | 1–12 |
| `day` | int/str | No | `"day"` | 1–31 |
| `hour`,`minute`,`second`,`millisecond` | int/str | No | igual | Para escala fina |
| `display_date` | str | No | `"display_date"` | Texto a mostrar en lugar de la fecha |
| `format` | str | No | `"format"` | Formato de fecha |

> Nota de compatibilidad: la API de TimelineJS también documenta `display_text` dentro del objeto fecha; el formato de datos/hoja de cálculo usa `display_date`. Este modelo emite `display_date`.

### 2.2 `Text`

| Campo | Requerido | Serializa | Notas |
|---|---|---|---|
| `headline` | No | `"headline"` | Título del slide |
| `text` | No | `"text"` | Cuerpo; **admite HTML** |

### 2.3 `Media`

| Campo | Serializa | Notas |
|---|---|---|
| `url` | `"url"` | Imagen, video, tweet, PDF, etc. (TimelineJS detecta el tipo) |
| `caption` | `"caption"` | |
| `credit` | `"credit"` | |
| `thumbnail` | `"thumbnail"` | Miniatura en el time-nav |
| `alt`,`title`,`link`,`link_target` | iguales | Accesibilidad y enlace |

### 2.4 `Background`

| Campo | Serializa | Notas |
|---|---|---|
| `url` | `"url"` | Imagen de fondo del slide |
| `color` | `"color"` | Hex o nombre CSS |

### 2.5 `Slide` (= `Event`)

**Propósito:** un slide del story-slider. Para **events**, `start_date` es obligatorio; para el **title**, no.

| Campo | Tipo | Requerido (event) | Serializa |
|---|---|---|---|
| `start_date` | TLDate/dict | Sí | `"start_date"` |
| `end_date` | TLDate/dict | No | `"end_date"` |
| `text` | Text/dict | No | `"text"` |
| `media` | Media/dict | No | `"media"` |
| `group` | str | No | `"group"` (fila en el time-nav) |
| `display_date` | str | No | `"display_date"` |
| `background` | Background/dict | No | `"background"` |
| `autolink` | bool | No | `"autolink"` |
| `unique_id` | str | No | `"unique_id"` (id estable para `change`/`goToId`) |

#### Validación

```python
Slide.validate(require_date=True)   # events  → exige start_date.year
Slide.validate(require_date=False)  # title   → no exige fecha
```

### 2.6 `Era`

| Campo | Requerido | Serializa |
|---|---|---|
| `start_date` | Sí | `"start_date"` |
| `end_date` | Sí | `"end_date"` |
| `text` | No | `"text"` |

### 2.7 `TimelineData` (raíz)

| Campo | Tipo | Default | Serializa |
|---|---|---|---|
| `events` | [Slide] | `[]` | `"events"` (siempre presente) |
| `title` | Slide? | `None` | `"title"` (omitido si None) |
| `eras` | [Era] | `[]` | `"eras"` (omitido si vacío) |
| `scale` | str? | `None` | `"scale"` (omitido si None) |

#### Reglas de validación

```
- scale ∈ {None, "human", "cosmological"}
- cada event: start_date.year presente
- title (si existe): no requiere fecha
```

## 3. Ejemplo Canónico (paridad con reflex_resume)

Entrada Python:

```python
TimelineData(events=[
    Event(
        start_date=TLDate(2024, 12, 14),
        media=Media(url="https://drive.google.com/file/d/ID/view",
                    credit="Anthropic Academy"),
        text=Text("Claude Code in Action", "Claude Code in Action"),
    ),
])
```

Salida JSON (idéntica a un evento de `assets/timeline.json`):

```json
{
  "events": [
    {
      "start_date": { "year": "2024", "month": "12", "day": "14" },
      "media": { "url": "https://drive.google.com/file/d/ID/view", "credit": "Anthropic Academy" },
      "text": { "headline": "Claude Code in Action", "text": "Claude Code in Action" }
    }
  ]
}
```

## 4. Operaciones Críticas

### Op1: Construir desde Python
`TimelineData(...).to_dict()` → dict JSON-serializable. Complejidad O(n) eventos.

### Op2: Cargar desde archivo
`load_timeline_data(path)` → lee JSON, `from_dict`, `validate()`. Usado para migrar el `timeline.json` existente (178 eventos).

### Op3: Round-trip (idempotencia)
`TimelineData.from_dict(raw).to_dict() == raw` para datos canónicos — verificado por test `test_from_dict_roundtrip`.

## 5. Migración de Datos

- No hay cambio de esquema: el `timeline.json` de `reflex_resume` se consume tal cual.
- Si en el futuro se agregan campos (p. ej. `location`), se añaden como atributos opcionales en `Slide`/`models.py` sin romper datos existentes.

## 6. Notas de Almacenamiento

- Los datos pueden vivir como: (a) objetos Python en código, (b) un `.json` en `assets/`, o (c) generados dinámicamente desde una base de datos y pasados como dict.

---

## Historial de Cambios

| Versión | Fecha | Autor | Cambios |
|---|---|---|---|
| 1.0 | 2026-06-14 | Ernesto Crespo | Versión inicial |
