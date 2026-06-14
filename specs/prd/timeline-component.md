# reflex-knightlab-timeline — Native TimelineJS Component

## Product Requirements Document (PRD)

| Campo | Valor |
|---|---|
| **Autor** | Ernesto Crespo |
| **Estado** | `APPROVED` |
| **Versión** | 1.0 |
| **Fecha** | 2026-06-14 |
| **Reviewers** | — |
| **Última actualización** | 2026-06-14 |

---

## 1. Resumen Ejecutivo

`reflex-knightlab-timeline` es un componente Reflex, instalable vía pip, que envuelve de forma nativa la librería JavaScript **Knight Lab TimelineJS**. Permite a un desarrollador Reflex declarar una línea de tiempo interactiva (certificaciones, hitos, historia de un proyecto) en Python puro, pasando datos como objetos tipados o como un diccionario/JSON, sin escribir HTML, iframes ni JavaScript.

El producto nace de **migrar** el timeline existente en el proyecto `reflex_resume`, que hoy se renderiza mediante un `iframe` apuntando a un `timeline.html` estático que carga TimelineJS desde el CDN y hace `fetch` de un `timeline.json`. Esa solución funciona pero está aislada del estado de la app, no es reutilizable y depende de archivos estáticos. El nuevo componente reemplaza ese patrón por un wrapper React/Reflex de primera clase, reactivo al estado y empaquetado para reutilizarse en cualquier proyecto Reflex.

## 2. Contexto y Problema

### 2.1 Situación Actual

En `reflex_resume`, la sección de certificaciones (`web/components/resume_sections.py::certifications_section`) renderiza:

```python
rx.el.iframe(src="/timeline.html", class_name="... h-[400px] md:h-[700px] ...")
```

`assets/timeline.html` carga el CSS/JS de TimelineJS desde `cdn.knightlab.com`, hace `fetch('/timeline.json')` e instancia `new TL.Timeline('timeline-embed', data, {...})`. Los datos viven en `assets/timeline.json` (178 eventos).

### 2.2 Problema

1. **Aislamiento por iframe:** el timeline no puede comunicarse con el estado de Reflex (no hay forma de reaccionar a `change`, navegación o zoom desde Python).
2. **No reutilizable:** la lógica está acoplada a archivos estáticos de un proyecto; no se puede instalar en otro proyecto Reflex.
3. **Dependencia de CDN y de archivos estáticos** servidos en rutas fijas (`/timeline.html`, `/timeline.json`).
4. **Sin tipado ni validación:** editar el JSON a mano es propenso a errores (comas, comillas, fechas como número en vez de string).

### 2.3 Oportunidad

Empaquetar TimelineJS como componente Reflex nativo, versionado vía npm, con builders tipados en Python y eventos enlazados al estado. Beneficia a cualquier desarrollador Reflex que necesite una línea de tiempo, y moderniza el caso de uso original (`reflex_resume`).

## 3. Usuarios Objetivo

### Persona 1: Desarrollador Reflex
- **Descripción:** construye apps full-stack en Python con Reflex.
- **Necesidad principal:** insertar una línea de tiempo interactiva con pocas líneas, sin tocar JS.
- **Frecuencia de uso:** eventual (por proyecto).
- **Nivel técnico:** medio/alto.

### Persona 2: Mantenedor de `reflex_resume` (Ernesto)
- **Descripción:** dueño del CV/portfolio en Reflex.
- **Necesidad principal:** migrar el timeline de certificaciones a un componente reutilizable, manteniendo paridad visual y de datos.
- **Frecuencia de uso:** mensual (agrega certificados).
- **Nivel técnico:** alto.

## 4. Objetivos y Métricas de Éxito

### 4.1 Objetivos del Producto

| Objetivo | Métrica | Target | Plazo |
|---|---|---|---|
| Sustituir el iframe por componente nativo | Paridad funcional con `timeline.html` | 100% de opciones soportadas | v0.1 |
| Reutilización | Instalable con `pip install` y usable en demo | Demo corre | v0.1 |
| Robustez de datos | Cobertura de tests del modelo de datos | > 90% | v0.1 |

### 4.2 Objetivos de Usuario

| Objetivo del Usuario | Indicador |
|---|---|
| Crear un timeline sin escribir JS | Una llamada `timeline(data=...)` |
| Reaccionar a navegación desde Python | Handler `on_change` actualiza el estado |
| Migrar datos existentes sin reescribir | `load_timeline_data("timeline.json")` |

## 5. Alcance

### 5.1 In Scope (Incluido)
- [x] Componente Reflex nativo que envuelve TimelineJS (npm `@knight-lab/timelinejs`).
- [x] Builders tipados: `TLDate`, `Text`, `Media`, `Background`, `Slide`/`Event`, `Era`, `TimelineData`.
- [x] Objeto `TimelineOptions` con **todas** las opciones documentadas de TimelineJS.
- [x] Carga de datos por: objeto Python, dict, o archivo JSON (`load_timeline_data`).
- [x] Eventos: `on_change`, `on_loaded`, `on_dataloaded`, `on_nav_next`, `on_nav_previous`, `on_zoom_in`, `on_zoom_out`, `on_back_to_start`.
- [x] App demo con paridad respecto a `reflex_resume` + timeline construido en Python + interactividad.
- [x] Empaquetado pip (`pyproject.toml`), tests (pytest), artefactos SDD.

### 5.2 Out of Scope (Excluido)
- Fuente de datos Google Sheets en vivo dentro del componente — razón: requiere CORS/red; el patrón recomendado es transformar a JSON. (Documentado como consideración futura.)
- Editor visual de timelines — fuera del propósito de un componente.
- Métodos imperativos de control (goTo, etc.) expuestos como API Python — consideración futura.

### 5.3 Futuras Consideraciones
- Exponer métodos de navegación (`go_to_next`, `go_to_id`) vía refs/imperative handle.
- Soporte directo de URL de Google Spreadsheet como `source`.
- Temas (`theme`) y fuentes empaquetadas localmente para uso offline total.

## 6. Requisitos Funcionales

### RF-001: Renderizar un timeline desde datos Python
- **Descripción:** El sistema debe renderizar una línea de tiempo TimelineJS a partir de un `TimelineData` o un dict.
- **Actor:** Desarrollador Reflex.
- **Precondiciones:** Componente instalado; app Reflex.
- **Flujo principal:**
  1. El desarrollador construye `TimelineData(events=[...])`.
  2. Llama `timeline(data=...)` dentro de una página.
  3. Reflex compila e instala `@knight-lab/timelinejs`.
  4. En el navegador, el wrapper instancia `new Timeline(div, data, options)`.
- **Postcondiciones:** El timeline interactivo aparece en la página.
- **Prioridad:** `MUST`

### RF-002: Configurar la presentación
- **Descripción:** El sistema debe aceptar todas las opciones documentadas de TimelineJS vía `TimelineOptions`.
- **Prioridad:** `MUST`

### RF-003: Reaccionar a eventos del timeline
- **Descripción:** El sistema debe permitir asociar event handlers de Reflex a los eventos de TimelineJS (mínimo `change`).
- **Flujo principal:** `timeline(data=..., on_change=State.handler)` → al cambiar de slide, el handler recibe el `unique_id`.
- **Prioridad:** `MUST`

### RF-004: Migrar datos existentes
- **Descripción:** El sistema debe cargar y validar un `timeline.json` existente.
- **Prioridad:** `MUST`

### RF-005: Validar datos
- **Descripción:** El sistema debe validar que cada evento tenga `start_date.year` y que `scale`/`timenav_position` sean valores válidos.
- **Prioridad:** `SHOULD`

## 7. Requisitos No Funcionales

### Rendimiento
- La serialización de datos (Python → dict) debe ser O(n) sobre el número de eventos; 178 eventos se serializan en milisegundos.

### Compatibilidad
- Python ≥ 3.10; Reflex ≥ 0.8.0; TimelineJS 3.9.x (pin a 3.9.11).
- SSR-safe: la instanciación de TimelineJS ocurre solo en cliente (dentro de `useEffect`).

### Mantenibilidad
- Cobertura de tests del modelo de datos > 90%; código modular (modelo / opciones / componente separados).

### Seguridad
- El `text`/`media.url` provienen del autor del timeline; el componente no introduce ejecución de código adicional más allá de lo que TimelineJS ya hace (que renderiza HTML en `text`). Documentar que `text` admite HTML y por tanto debe provenir de fuentes confiables.

## 8. Restricciones y Dependencias

### Restricciones Técnicas
- TimelineJS es **imperativo** (clase `TL.Timeline`), no un componente React → requiere wrapper con `ref` + `useEffect`.
- Necesita un contenedor con dimensiones explícitas (width/height).

### Dependencias Externas

| Dependencia | Tipo | Owner | Estado | Riesgo |
|---|---|---|---|---|
| `@knight-lab/timelinejs` | npm | Knight Lab | Estable (3.9.11) | Bajo |
| `reflex` | pip | Reflex.dev | Estable (≥0.8) | Bajo |

## 9. User Stories

### Épica: Componente de línea de tiempo reutilizable

**US-001:** Como desarrollador Reflex, quiero llamar `timeline(data=...)` para mostrar una línea de tiempo, para no tener que escribir HTML/JS.
- Criterios de aceptación:
  - [x] `timeline(data=TimelineData(...))` renderiza sin error.
  - [x] El paquete se instala con pip.

**US-002:** Como mantenedor de `reflex_resume`, quiero cargar mi `timeline.json` actual, para migrar sin reescribir los 178 certificados.
- Criterios de aceptación:
  - [x] `load_timeline_data("timeline.json")` produce un `TimelineData` válido.
  - [x] La demo muestra los 178 eventos.

**US-003:** Como desarrollador, quiero reaccionar al cambio de slide en Python, para sincronizar otra parte de la UI.
- Criterios de aceptación:
  - [x] `on_change` recibe el `unique_id` del slide actual.

## 10. Wireframes / Mockups
- La presentación visual es la de TimelineJS (story slider arriba, time-navigator abajo). Ver demo `timeline_demo`.

## 11. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Forma de export ESM/CJS de TimelineJS varía | Media | Alto | Resolución de la clase con varios *fallbacks* en el wrapper |
| Acceso a `window` rompe SSR | Media | Alto | Instanciar dentro de `useEffect` (solo cliente) |
| Ruta del CSS del paquete cambia entre versiones | Baja | Medio | Pin de versión 3.9.11 + verificación de la ruta `dist/css/timeline.css` |

## 12. Timeline Estimado

| Fase | Duración Estimada | Entregable |
|---|---|---|
| Spec & Design | 0.5 día | Specs aprobados |
| Implementación (TDD) | 1 día | Componente + tests verdes |
| Demo & Docs | 0.5 día | Demo + README |

---

## Historial de Cambios

| Versión | Fecha | Autor | Cambios |
|---|---|---|---|
| 1.0 | 2026-06-14 | Ernesto Crespo | Versión inicial |

## Aprobaciones

| Rol | Nombre | Fecha | Estado |
|---|---|---|---|
| Product Owner | Ernesto Crespo | 2026-06-14 | ☑ Aprobado |
| Tech Lead | Ernesto Crespo | 2026-06-14 | ☑ Aprobado |
