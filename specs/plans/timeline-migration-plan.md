# reflex-knightlab-timeline — Implementation Plan

## Metadata

| Campo | Valor |
|---|---|
| **Autor** | Ernesto Crespo |
| **Estado** | `COMPLETED` |
| **Versión** | 1.0 |
| **Fecha** | 2026-06-14 |
| **PRD** | `../prd/timeline-component.md` |
| **Tech Design** | `../technical/timeline-architecture.md` |
| **Data Model** | `../data-model/timeline-schema.md` |
| **API Spec** | `../api/timeline-component-api.md` |

---

## 1. Resumen de Implementación

Migración del timeline de `reflex_resume` (iframe + `timeline.html` + `timeline.json`) a un componente Reflex nativo, empaquetado y reutilizable, siguiendo **TDD**: tests primero (red), implementación después (green). 4 fases cortas. Duración real: ~1 día.

**Equipo:** 1 desarrollador. **Estado:** completado en v0.1.

## 2. Pre-requisitos

| Pre-requisito | Owner | Estado |
|---|---|---|
| Investigar API de TimelineJS (opciones, eventos, JSON) | Ernesto | ☑ |
| Investigar wrapping de libs JS en Reflex | Ernesto | ☑ |
| Confirmar npm `@knight-lab/timelinejs@3.9.11` y rutas dist | Ernesto | ☑ |

## 3. Fases de Implementación

### Fase 1: Foundation & Scaffolding

**Objetivo:** estructura del paquete y configuración.

| ID | Tarea | Estimación | Dependencia | Estado |
|---|---|---|---|---|
| F1-01 | Estructura del repo (`custom_components/`, `tests/`, `specs/`, `timeline_demo/`) | 0.5h | — | ☑ |
| F1-02 | `pyproject.toml` (paquete pip + config pytest) | 0.5h | F1-01 | ☑ |
| F1-03 | `.gitignore`, `LICENSE` (MIT) | 0.25h | F1-01 | ☑ |

**Done:** el repo importa `reflex_knightlab_timeline`; pytest detecta `tests/`.

### Fase 2: TDD — Tests primero (RED)

**Objetivo:** definir el contrato antes de implementar.

| ID | Tarea | Estimación | Dependencia | Estado |
|---|---|---|---|---|
| F2-01 | `test_models.py` (TLDate, Text, Media, Slide, Era, TimelineData, load) | 1h | F1-02 | ☑ |
| F2-02 | `test_options.py` (todas las opciones, validación, paridad iframe) | 0.5h | F1-02 | ☑ |
| F2-03 | `test_component.py` (tag, deps, imports, custom code, eventos, create) | 0.5h | F1-02 | ☑ |
| F2-04 | Ejecutar suite → confirmar RED | 0.1h | F2-01..03 | ☑ |

**Done:** los tests fallan por falta de implementación (estado red confirmado).

### Fase 3: Core — Implementación (GREEN)

**Objetivo:** llevar los tests a verde.

| ID | Tarea | Estimación | Dependencia | Estado |
|---|---|---|---|---|
| F3-01 | `models.py` (builders + validación + `from_dict`/`load_timeline_data`) | 1.5h | F2-04 | ☑ |
| F3-02 | `options.py` (`TimelineOptions` + `to_dict` + mapeo `trackResize`) | 0.5h | F2-04 | ☑ |
| F3-03 | `timeline.py` (`KnightLabTimeline` + wrapper JS + eventos + `create`) | 2h | F3-01, F3-02 | ☑ |
| F3-04 | `__init__.py` (API pública, import protegido del componente) | 0.25h | F3-03 | ☑ |
| F3-05 | Ejecutar suite → 43/43 GREEN | 0.25h | F3-01..04 | ☑ |

**Done:** 43 tests verdes (33 datos + 10 contrato del componente).

### Fase 4: Demo, Docs & Verificación

**Objetivo:** demostrar paridad e integración; documentar.

| ID | Tarea | Estimación | Dependencia | Estado |
|---|---|---|---|---|
| F4-01 | Copiar `timeline.json` (178 eventos) a `timeline_demo/assets/` | 0.1h | F3-05 | ☑ |
| F4-02 | App demo: timeline en Python + paridad resume + `on_change` en vivo | 1h | F4-01 | ☑ |
| F4-03 | `README.md` (uso, instalación, migración) | 0.5h | F3-05 | ☑ |
| F4-04 | Artefactos SDD (PRD, Tech, Data, API, Plan, Migración) | 1h | F3-05 | ☑ |
| F4-05 | Verificación: render del componente + suite final + smoke de la demo | 0.5h | F4-02 | ☑ |

**Done:** demo construye ambos timelines; render del componente emite el wrapper y las dependencias; suite verde.

## 4. Mapa de Dependencias

```
Fase 1 (scaffold)
  └─► Fase 2 (tests RED)
        └─► Fase 3 (impl GREEN)
              └─► Fase 4 (demo + docs + verify)
```

## 5. Riesgos de Implementación

| Riesgo | Prob. | Impacto | Mitigación | Estado |
|---|---|---|---|---|
| Export ESM/CJS de TimelineJS | Media | Alto | Resolución con fallbacks en el wrapper | Mitigado |
| Ruta del CSS del paquete | Baja | Medio | Verificada `dist/css/timeline.css` vía listado del paquete | Mitigado |
| SSR rompe por `window` | Media | Alto | Import dinámico en `useEffect` | Mitigado |

## 6. Definición de Done (Global)

- [x] Código implementado en `custom_components/reflex_knightlab_timeline/`.
- [x] Tests verdes (datos + contrato del componente) — 43/43.
- [x] Demo que reproduce el caso de `reflex_resume` (paridad de 178 eventos).
- [x] README y artefactos SDD completos.
- [x] Repo inicializado con git.

---

## Historial de Cambios

| Versión | Fecha | Autor | Cambios |
|---|---|---|---|
| 1.0 | 2026-06-14 | Ernesto Crespo | Versión inicial (implementación completada) |
