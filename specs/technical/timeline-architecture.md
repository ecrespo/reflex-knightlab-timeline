# reflex-knightlab-timeline — Technical Design Document

## Metadata

| Campo | Valor |
|---|---|
| **Autor** | Ernesto Crespo |
| **Estado** | `APPROVED` |
| **Versión** | 1.0 |
| **Fecha** | 2026-06-14 |
| **PRD Relacionado** | `../prd/timeline-component.md` |
| **API Spec Relacionado** | `../api/timeline-component-api.md` |
| **Data Model Relacionado** | `../data-model/timeline-schema.md` |

---

## 1. Contexto

TimelineJS3 expone una clase **imperativa** `TL.Timeline(container, data, options)` que manipula el DOM directamente y usa `window`/`document`. No es un componente React. Reflex, en cambio, compila componentes Python a React/Next.js con SSR. El reto técnico central es envolver una librería imperativa, que no es SSR-safe, dentro del modelo declarativo y reactivo de Reflex, de modo que:

1. La instanciación ocurra solo en el cliente (no en SSR).
2. Los datos y opciones fluyan desde el estado de Reflex (Python) hacia la instancia de TimelineJS.
3. Los eventos de TimelineJS (`change`, `nav_next`, …) reboten hacia event handlers de Reflex.

La estrategia es definir un **componente React funcional propio** (inyectado como *custom code*) que posee un `ref` a un `div` y, dentro de `useEffect`, importa dinámicamente TimelineJS e instancia la clase sobre ese nodo. El componente Reflex (`KnightLabTimeline`) referencia ese tag local y declara props/eventos tipados.

## 2. Objetivos Técnicos

- **Correctitud:** los datos Python serializan exactamente al JSON que TimelineJS espera (fechas como string, campos opcionales omitidos).
- **SSR-safe:** ningún acceso a `window` en render del servidor; instanciación diferida a `useEffect`.
- **Reactividad:** cambios en `data`/`options` re-inicializan el timeline.
- **Mantenibilidad:** capa de datos pura (testeable sin Reflex), separada del componente.

## 3. Arquitectura Propuesta

### 3.1 Diagrama de Alto Nivel

```
┌────────────────────────────┐
│  Python (Reflex app)        │
│                             │
│  TimelineData / Options ────┼──► .to_dict() (JSON-serializable)
│  timeline(data=..., on_*=..)│
└──────────────┬──────────────┘
               │ compila
               ▼
┌────────────────────────────────────────────┐
│  React / Next.js (generado por Reflex)       │
│                                              │
│  <KnightLabTimeline data={...} options={...} │
│        onChange={...}/>   (custom-code FC)    │
│        │                                      │
│        ├─ useRef(div)                         │
│        └─ useEffect:                          │
│             import("@knight-lab/timelinejs")  │
│             new Timeline(div, data, options)  │
│             tl.on("change", ...) ─► onChange  │
└──────────────┬───────────────────────────────┘
               │ instancia (solo cliente)
               ▼
        ┌──────────────────┐
        │  TimelineJS 3.9   │  (DOM imperativo + CSS del npm)
        └──────────────────┘
```

### 3.2 Componentes

| Componente | Tecnología | Responsabilidad |
|---|---|---|
| `models.py` | Python (dataclasses) | Builders tipados → JSON de TimelineJS; validación; parsing/round-trip |
| `options.py` | Python (dataclass) | Todas las opciones de presentación → dict |
| `timeline.py` | Reflex `rx.Component` + custom JS | Wrapper React (ref+useEffect), props/eventos, instalación npm |
| Wrapper FC (`_WRAPPER_JS`) | React (JS) | Instancia imperativa, cleanup, puente de eventos |
| `timeline_demo/` | Reflex app | Demostración y prueba de integración |

### 3.3 Flujo de Datos

**Flujo: renderizar y navegar un timeline**

```
1. Python construye TimelineData → .to_dict() → prop `data` (objeto JS literal).
2. Reflex compila <KnightLabTimeline data=... options=... onChange=...>.
3. add_imports() registra: CSS de TimelineJS + hooks de React; lib_dependencies fija @knight-lab/timelinejs@3.9.11 en package.json.
4. En cliente, useEffect: import("@knight-lab/timelinejs"); resuelve la clase Timeline.
5. new Timeline(divRef, data, options).
6. tl.on("change", d => onChange(d.unique_id)) → evento Reflex → State handler en Python.
7. Si data/options cambian (dep [JSON.stringify(data), JSON.stringify(options)]) → cleanup (vacía el div) + reinstanciación.
```

**Flujo de error / compensación:**

```
1. Si la clase Timeline no se resuelve → console.error y return (no crash).
2. Si `new Timeline(...)` lanza → try/catch, console.error, return.
3. Si el import dinámico falla → .catch(console.error).
4. Cleanup en unmount/cambio de deps → evita timelines duplicados/fugas.
```

## 4. Decisiones de Diseño

### DD-001: Wrapper imperativo vía custom code en lugar de `tag` npm directo

- **Decisión:** definir un componente React local (custom code) con `useRef`+`useEffect`, en vez de mapear `tag="Timeline"` a la clase del paquete.
- **Contexto:** TimelineJS exporta una **clase**, no un componente React. Si Reflex generara `<Timeline .../>`, React intentaría renderizar una clase no-React y fallaría.
- **Alternativas evaluadas:**

| Opción | Pros | Contras |
|---|---|---|
| **A (elegida): wrapper FC en custom code** | Funciona con libs imperativas; control total de ciclo de vida y eventos | Algo de JS embebido en Python |
| B: `tag="Timeline"` con `library` npm | Menos código | No funciona: la clase no es un componente React |
| C: iframe (status quo) | Trivial | Aislado del estado, no reutilizable (es justo lo que migramos) |

- **Justificación:** es el patrón estándar de Reflex para envolver librerías que requieren un nodo DOM y APIs de navegador.
- **Consecuencias:** el componente lleva un bloque JS mantenido a mano; cubierto por tests de contrato (verifican que el wrapper se inyecta y referencia la API correcta).

### DD-002: Import dinámico dentro de `useEffect` (SSR-safe)

- **Decisión:** `import("@knight-lab/timelinejs")` perezoso dentro del efecto, no en el top-level del módulo.
- **Contexto:** TimelineJS toca `window`/`document` al cargar; un import estático correría en SSR.
- **Alternativas:** `NoSSRComponent` con `dynamic(import(...))` — válido para componentes React, pero aquí el tag es local (custom code), así que el patrón natural es el import dinámico dentro del efecto.
- **Consecuencias:** cero acceso a navegador en el servidor; el `div` se renderiza vacío en SSR y se hidrata en cliente.

### DD-003: Instalación del paquete vía `lib_dependencies` + import de CSS

- **Decisión:** fijar `lib_dependencies=["@knight-lab/timelinejs@3.9.11"]` y además importar el CSS (`add_imports`).
- **Contexto:** al no usar `library`, hay que garantizar que npm instale el paquete y su versión.
- **Justificación:** `lib_dependencies` fija la versión; el import del CSS (clave `""`) añade el paquete como dependencia y trae los estilos. Doble garantía.

### DD-004: Capa de datos pura, separada del componente

- **Decisión:** `models.py`/`options.py` no importan Reflex.
- **Justificación:** permite TDD rápido sin runtime de Reflex y reutilización fuera de Reflex; el `__init__` importa el componente de forma protegida.

## 5. Patrones y Convenciones

### 5.1 Estructura del Código

```
reflex-knightlab-timeline/
├── custom_components/
│   └── reflex_knightlab_timeline/
│       ├── __init__.py        # API pública (import protegido del componente)
│       ├── models.py          # builders de datos (sin Reflex)
│       ├── options.py         # opciones de presentación (sin Reflex)
│       └── timeline.py        # rx.Component + wrapper JS
├── timeline_demo/             # app Reflex de demostración
│   ├── assets/timeline.json   # datos migrados de reflex_resume (178 eventos)
│   ├── rxconfig.py
│   └── timeline_demo/timeline_demo.py
├── tests/                     # pytest (TDD)
│   ├── test_models.py
│   ├── test_options.py
│   └── test_component.py
├── specs/                     # artefactos SDD
├── pyproject.toml
└── README.md
```

### 5.2 Patrones Aplicados

| Patrón | Dónde | Por qué |
|---|---|---|
| Builder + `to_dict()` | `models.py`, `options.py` | Serialización explícita y testeable |
| Adapter (imperativo→declarativo) | wrapper FC | Adaptar TimelineJS a React/Reflex |
| Null-object/omisión | `to_dict()` omite `None` | Dejar que TimelineJS use sus defaults |
| Lazy import | `useEffect` | SSR-safety |

### 5.3 Manejo de Errores

```python
# Validación de dominio (Python)
class ValueError: ...   # event sin start_date.year; scale/timenav_position inválidos
```

```javascript
// Cliente: defensivo, nunca rompe el render
try { new TimelineClass(el, data, options); } catch (e) { console.error(e); }
```

## 6. Seguridad

### 6.1 Superficie

| Vector | Mitigación |
|---|---|
| `text` admite HTML (TimelineJS lo renderiza) | Documentar que el contenido debe provenir de fuentes confiables; no se introduce sink adicional |
| Carga de recursos remotos (media URLs) | Igual comportamiento que TimelineJS estándar; responsabilidad del autor de datos |

### 6.2 Datos Sensibles
- No aplica: el componente no maneja credenciales ni PII por diseño.

## 7. Observabilidad

- Errores del cliente se emiten con prefijo `[reflex-knightlab-timeline]` vía `console.error`, distinguibles en la consola del navegador.
- La opción `debug=True` de TimelineJS habilita logging interno detallado.

## 8. Testing Strategy

| Nivel | Cobertura Target | Herramientas | Qué cubre |
|---|---|---|---|
| Unit (datos) | > 90% | pytest | `models.py`, `options.py`: serialización, validación, round-trip |
| Contrato (componente) | Contrato clave | pytest + reflex | tag/deps/imports/custom-code/eventos/creación |
| Integración manual | Happy path | demo `reflex run` | render real en navegador, navegación, `on_change` |

Enfoque **TDD**: los tests se escribieron primero (estado *red*), luego la implementación los llevó a *green* (43 tests).

## 9. Plan de Migración / Rollout

### 9.1 Estrategia
- El componente vive en su propio repo `reflex-knightlab-timeline`, independiente de `reflex_resume`.
- `reflex_resume` puede adoptar el componente reemplazando el `iframe` por `timeline(data=load_timeline_data(...))` (ver `../migration/iframe-to-native.md`). Esta migración del consumidor es opcional y no rompe nada existente.

### 9.2 Backward Compatibility
- El formato de datos es el mismo JSON de TimelineJS; el `timeline.json` actual funciona sin cambios.

## 10. Preguntas Abiertas
- [ ] ¿Exponer métodos imperativos (goTo/goToId) vía `imperative handle`? — Owner: Ernesto, post-v0.1.
- [ ] ¿Soporte directo de Google Sheets como `source`? — Owner: Ernesto, post-v0.1.

---

## Historial de Cambios

| Versión | Fecha | Autor | Cambios |
|---|---|---|---|
| 1.0 | 2026-06-14 | Ernesto Crespo | Versión inicial |
