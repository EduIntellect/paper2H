# Auditoría remota H* / censura / cota teórica — organización `fedeg-umh-es`

**ROJO estructural (15/16 repos bloqueados) — con 1 repo confirmado en ÁMBAR (`varret-pm10-paper`, verificado con evidencia reproducible vía Codex)**

> Actualización: la atribución a `varret-pm10-paper` que en la versión anterior de este informe era una hipótesis sin confirmar, **quedó confirmada** con acceso de solo lectura al repo (§8): script real localizado y citado por líneas, conteos de fusión modelo↔persistencia verificados, y un bug de comparación (no del pipeline) identificado y corregido. El resto de la organización (15 repos) sigue sin poder inspeccionarse desde ninguna sesión de Claude Code por el bloqueo de scope descrito en §0.

---

## 0. Qué pudo hacerse y qué no (esta sesión de Claude Code)

Esta sesión está anclada al owner `eduintellect` (fuente `eduintellect/paper2h`). El servidor MCP de GitHub de esta sesión permite `search_repositories` (búsqueda global) pero **deniega** `get_file_contents`, `list_branches`, `list_commits`, etc. sobre cualquier repo no "configurado" en la sesión, y `add_repo` rechazó explícitamente los 16 repos de `fedeg-umh-es`:

```
add_repo: cross-tier adds are not supported in v1: requested "fedeg-umh-es/<repo>"
but session already has repos from owner(s) [eduintellect]. Start a new session
with the requested repo as the initial source...
```

No existe en esta sesión herramienta para crear sesiones nuevas ni `gh` CLI. Por tanto:

- **Fase 0 (descubrimiento)**: completa. 16 repos confirmados vía `search_repositories` (metadata: nombre, descripción, visibilidad, fecha de push). Ver tabla §1.
- **Fase 1/2 (datos y código) directas desde esta sesión**: **bloqueadas** para los 16 repos — cero acceso propio a árboles, ficheros o contenido.
- **Verificación indirecta pero confirmada (§8)**: se encargó a una sesión de Codex, con acceso de solo lectura a una copia local de `fedeg-umh-es/varret-pm10-paper`, repetir y ampliar el análisis. A diferencia de la primera ronda (evidencia de segunda mano sin atribución confirmada), esta segunda ronda aporta citas de código por línea, conteos de fusión reproducibles y confirmación cruzada contra ficheros versionados del propio repo (`skill_summary_*.csv`). Se trata como evidencia sólida, aunque sigue sin ser una verificación *directa* de esta sesión de Claude Code.
- El intento de `git clone` de Codex contra GitHub falló por proxy (`CONNECT tunnel failed, 403`); el análisis se hizo contra una copia local ya presente en `/workspace/varret-pm10-paper`, copiada a `/tmp/codex_hstar_audit/clones/varret-pm10-paper_localcopy`. No se ha verificado que esa copia local coincida byte a byte con `HEAD` remoto — hueco menor de procedencia, anotado en `missing_items`.

---

## 1. Fase 0 — Inventario (16 repos, metadata únicamente salvo el confirmado en §8)

| Repo | Último push | Visibilidad | Motivo de inclusión | Estado |
|---|---|---|---|---|
| varret-pm10-paper | 2026-06-04 | público | pm10, rolling-origin, skill, "diagnostic" | **Confirmado, ver §8** |
| PM10-Horizons-Diagnostic | 2026-04-15 | internal | pm10, horizon | No inspeccionado |
| madrid-pm10-rank-reversal | 2026-04-14 | internal | pm10 | No inspeccionado |
| Hstar_PM10_PM25_Madrid_Valencia | 2026-04-28 | público | hstar, pm10, pm25 | No inspeccionado |
| P32_IJF_GhostSkill_Hstar | 2026-04-27 | público | skill, hstar | No inspeccionado |
| P1_PM10_Meteorology_Hstar | 2026-05-29 | internal | pm10, hstar | No inspeccionado |
| hstar | 2026-04-01 | internal | hstar | No inspeccionado |
| hstar-p3-prob-operational-probabilistic-predictability | 2026-04-11 | internal | hstar, predictability | No inspeccionado |
| P33_variance_collapse | 2026-04-17 | público | variance (skill-adyacente) | No inspeccionado |
| P34_forecasting_library | 2026-04-17 | público | forecast (librería) | No inspeccionado |
| p34-variance-retention-api | 2026-05-14 | público | variance-retention (API) | No inspeccionado |
| paper_c_kge_variance | 2026-05-04 | público | variance, kge (métrica) | No inspeccionado |
| e2-met-validation | 2026-04-13 | internal | "PM10 Madrid 2015-2024" | No inspeccionado |
| GB-style | 2026-05-31 | público | sin coincidencia de keywords | Irrelevante, no auditado |
| ltw | 2026-04-18 | público | sin coincidencia de keywords (C) | Irrelevante, no auditado |
| Code2_AI | 2026-03-28 | internal | sin coincidencia de keywords | Irrelevante, no auditado |

---

## 2. Fase 1 y Fase 2 — Datos y código

**15/16 repos**: sin cambios respecto a la versión anterior — bloqueo total de scope, cero evidencia propia.

**`varret-pm10-paper` (confirmado)**:

| Ruta | Tipo | Confirmado por |
|---|---|---|
| `data/raw/pm10_daily.csv` (Elche), `pm10_valencia_vivers.csv`, `pm10_zarra_emep.csv` | series crudas | lectura directa, usadas para recalcular ACF/AR(1) hasta h=30 |
| `outputs/metrics/predictions.csv` (+ variantes por estación) | predicciones | filas `model` ∈ {`hgb_direct`, `ridge_direct`, `sarima`, `persistence`, …}, claves `origin_date` + `date` + `horizon` |
| `outputs/metrics/skill_summary_valencia_vivers.csv`, `skill_summary_zarra_emep.csv` | resumen versionado | `cat` directo — ya reportan skill RMSE positivo para `hgb_direct`/`ridge_direct` en todos los h, consistente con el resultado corregido |
| `scripts/01_generate_e1_rr_lags_only_predictions.py` | generador canónico | inspeccionado por línea (`nl -ba ... sed -n`); **no** es `test_cota_teorica_skill.py` (ese script no existe en el repo — fue una herramienta ad hoc de la ronda anterior) |

Hallazgos clave del código real:

- `HORIZONS = tuple(range(1, 8))` — **el límite h=1..7 está hardcodeado en el generador**, no es un artefacto del script de prueba ad hoc de la ronda anterior. Docstring confirma: *"horizon range h=1,...,7 days"*, *"train-only fitting at each origin"*, *"persistence as mandatory baseline"*.
- Las filas de persistencia se generan **dentro del mismo CSV** (`model == "persistence"`), no en una columna aparte — confirmado en el generador.
- El cálculo de skill oficial (`_build_skill_summary`) fusiona modelo y persistencia **por claves `origin_date` + `date`**, no por posición.

`origin_date` es, en la práctica, el identificador de origen de la evaluación rolling-origin — más fino que un "fold" agregado. Esto cambia la respuesta a varias preguntas de la Fase 3 (ver abajo).

---

## 3. Fase 3 — Cruce de evidencia (actualizada)

**1. ¿Existe skill_h por fold y horizonte en disco remoto?**
15/16 repos: no determinable (bloqueo). En `varret-pm10-paper` (confirmado): **sí, a nivel de origen individual** (`origin_date` × `horizon`) para `hgb_direct` y `ridge_direct`, en las 3 estaciones — más granular que "por fold". No hay agregación explícita en folds nombrados, pero `origin_date` permite reconstruirla.

**2. ¿Cuál es Hmax por dominio?**
Hmax = 7 confirmado como **límite hardcodeado del pipeline de producción** (`HORIZONS = tuple(range(1, 8))`), no un límite del script de prueba. Igual en las 3 estaciones.

**3. ¿Se puede saber si skill(Hmax) > 0 en cada fold sin reentrenar?**
Sí, con el merge correcto por claves, para `hgb_direct` y `ridge_direct` en las 3 estaciones a nivel de horizonte agregado (ver §8). No se ha desglosado explícitamente por `origin_date` individual en este informe, pero los datos para hacerlo están en disco.

**4. ¿Cuántos dominios tienen perfil completo (skill por fold/origen y horizonte)?**
**3** — Elche, Valencia Vivers y Zarra EMEP, en `varret-pm10-paper`, para h=1..7. Más allá de h=7: **ninguno** (bloqueado, requiere reentrenar — confirmado arquitectónicamente, no solo sospechado).

**5. ¿Hay predicciones crudas y_true/y_pred por fold y horizonte?**
Sí, confirmado: `predictions*.csv` trae `y_true` e `y_pred` por `origin_date`, `date`, `horizon` y `model` (incluida persistencia), con conteos de filas idénticos entre modelo y persistencia en `hgb_direct`/`ridge_direct` (ver tabla de merge en §8).

**6. ¿Está disponible la serie objetivo cruda con índice temporal y los rangos train/test por fold?**
Serie cruda: sí, confirmada. Rangos train/test explícitos por origen: **no confirmados como columnas propias** — el docstring dice "train-only fitting at each origin", lo que implica una partición por origen, pero no se ha localizado un fichero de particiones explícito (train_start/train_end/test_start/test_end).

**7. [Extra] ¿Multidominio (Pekín PM2.5, eólica, tráfico) en la organización?**
Sin cambios: no confirmado en ningún repo de `fedeg-umh-es`. Ese multidominio vive en `eduintellect/paper2h` (otro owner, fuera de alcance).

**8. [Extra] ¿`benchmark-pm-hstar` renombrado en `P34_forecasting_library` o `hstar`?**
Sin cambios: no determinable, ambos repos siguen bloqueados.

---

## 4. Interpretación de la evidencia confirmada

**Elche y Zarra EMEP — extensión de la cota teórica a h=30 (empírico bloqueado, confirmado):**

- Ninguna de las dos series muestra la cota ACF decayendo hacia cero en el rango h=8–30; en Elche la cota ACF se mueve entre 0.52 y 0.57, en Zarra EMEP entre 0.50 y 0.55. **Nada en la cota teórica sugiere que el skill real vaya a cruzar a cero pronto** — el techo teórico sigue muy por encima de lo alcanzado en h=7.
- El chequeo de periodicidad semanal (h=7, 14, 21 vs. vecinos) **no encontró pico dominante** en ninguna de las dos series — descarta estacionalidad semanal como explicación alternativa.
- El skill empírico más allá de h=7 sigue **genuinamente bloqueado**: confirmado por código (no por falta de tiempo) que el generador solo produce h=1..7, y extenderlo exige reentrenar con horizontes nuevos. **Este es ahora un ítem de coste (iii) —"requiere reentrenar"— confirmado, no solo sospechado.**

**Valencia Vivers — diagnóstico y corrección:**

El resultado de la ronda anterior ("skill_emp negativo en todo el rango, -1.58 a -0.36") **no se reproduce** con el pipeline canónico. Causa raíz identificada: la reconstrucción manual de la columna `baseline` hecha en la ronda anterior (fuera del repo, en `/tmp`, para poder ejecutar un script de prueba ad hoc) no respetó el emparejamiento por `origin_date` + `date` que usa el pipeline real — probablemente emparejó por posición o mezcló horizontes/modelos.

Con el merge correcto por claves, Valencia Vivers da:

| Modelo | h=1 | h=3 | h=5 | h=7 |
|---|---|---|---|---|
| hgb_direct | 0.142 | 0.350 | 0.403 | 0.411 |
| ridge_direct | 0.182 | 0.366 | 0.425 | 0.442 |

Positivo y creciente con h, con forma muy similar a Elche — consistente con el resumen ya versionado en el repo (`skill_summary_valencia_vivers.csv`, en escala RMSE, también positivo). **Conclusión: Valencia Vivers no tiene un problema real de skill negativo — el hallazgo anterior era un artefacto de mi propia reconstrucción manual, no del pipeline ni de la estación.** Dato aparte: se detectó que un modelo distinto, `stl_ridge_direct`, sí predice con un sesgo de escala fuerte (media ≈45 µg/m³ frente a y_true ≈22 µg/m³) — irrelevante para `hgb_direct`/`ridge_direct`, pero a evitar si se usa ese modelo en análisis futuros.

Conteos de fusión modelo↔persistencia (`hgb_direct`, `ridge_direct`, Valencia Vivers): filas modelo = filas persistencia = filas merge = filas válidas en los 7 horizontes — sin pérdida diferencial ni missing values que invaliden la comparación.

---

## 5. Qué falta, por coste ascendente (actualizado)

**(i) Recomputable en minutos** — resuelto en esta ronda:
- ~~Confirmar esquema de predictions.csv~~ → hecho.
- ~~Diagnóstico de Valencia Vivers~~ → hecho, causa raíz identificada y corregida.
- Pendiente: repetir el mismo diagnóstico de merge en Elche y Zarra EMEP (solo se confirmó explícitamente para Valencia Vivers) y aplicar la misma extensión teórica h=8–30 ya generada para Valencia Vivers (`theoretical_valencia_vivers_h1_30.csv` fue generado pero su contenido no se ha compartido todavía — pendiente de revisión).
- Verificar que la copia local usada por Codex (`/workspace/varret-pm10-paper`) coincide con `HEAD` remoto (el `git clone` falló por proxy, no se pudo confirmar directamente).

**(ii) Requiere descargar/inspeccionar datos** (bloqueado hasta nueva sesión de Claude Code con owner `fedeg-umh-es`):
- Fase 0-2 completas para los 15 repos restantes.
- Buscar fichero de particiones train/test explícito (o confirmar que `origin_date` es la única fuente de verdad).
- Resolver preguntas 7 y 8.

**(iii) Requiere reentrenar** — confirmado, no solo sospechado:
- Extender el horizonte empírico más allá de h=7 en cualquiera de las 3 estaciones de `varret-pm10-paper` exige reentrenar con horizontes nuevos (`HORIZONS` hardcoded en el generador).

---

## 6. Tabla de disponibilidad (actualizada)

| Dominio | Repo | Hmax | skill(origen,h) h≤7 | y_true/y_pred | Serie cruda | Particiones | Censura detectable h≤7 | Extensión h>7 |
|---|---|---|---|---|---|---|---|---|
| Elche (PM10) | varret-pm10-paper (confirmado) | 7 (hardcoded) | Sí | Sí | Sí | Implícita (`origin_date`), sin columnas explícitas | Sí — compatible, cota teórica sin decaer hasta h=30 | Bloqueada, requiere reentrenar |
| Valencia Vivers (PM10) | varret-pm10-paper (confirmado) | 7 (hardcoded) | Sí | Sí | Sí | Implícita, sin columnas explícitas | Sí — compatible (corregido: skill 0.14–0.44, ya no negativo) | Bloqueada, requiere reentrenar; tabla teórica h=8–30 generada pero no revisada aún |
| Zarra EMEP (PM10) | varret-pm10-paper (confirmado) | 7 (hardcoded) | Sí | Sí | Sí | Implícita, sin columnas explícitas | Sí — compatible, margen pequeño, cota teórica sin decaer hasta h=30 | Bloqueada, requiere reentrenar |
| 15 repos restantes | fedeg-umh-es/* | — | No determinable | No determinable | No determinable | No determinable | No determinable | No determinable — bloqueo de acceso |

---

## 7. Veredicto final (actualizado)

**ROJO estructural a nivel de organización** (15/16 repos siguen sin poder inspeccionarse desde ninguna sesión de Claude Code), **con `varret-pm10-paper` en ÁMBAR confirmado**: para sus 3 dominios PM10 existe skill reconstruible por origen y horizonte sin reentrenar dentro de h≤7, con evidencia reproducible (código citado, conteos de merge, contraste contra ficheros versionados). La censura por la derecha en H* es **compatible en las 3 estaciones** dentro de lo medible, pero **confirmar el verdadero H*** exige reentrenar más allá de h=7 — esto ya no es una incógnita, es un requisito arquitectónico confirmado.

**Corrección relevante sobre la ronda anterior**: el hallazgo "Valencia Vivers tiene skill negativo, revisar metodología" **era un falso positivo causado por mi propia reconstrucción manual de la columna baseline**, no un problema del pipeline auditado. Queda corregido en este informe.

**Acción mínima para desbloquear el resto de la organización**: abrir una sesión de Claude Code con un repo de `fedeg-umh-es` como fuente inicial y repetir Fases 0-2 con acceso real.

---

## 8. Apéndice — evidencia de la verificación vía Codex

Resumen de lo ejecutado (sin push, sin commit, sin modificar el repo; todo intermedio en `/tmp/codex_hstar_audit/`):

- Repo confirmado por grep de rutas exactas en el árbol: `fedeg-umh-es/varret-pm10-paper`.
- `test_cota_teorica_skill.py` no existe en el repo — confirmado que era una herramienta ad hoc de la ronda anterior, no parte del pipeline.
- Cota teórica (AR1, ACF) recalculada h=1–30 para Elche y Zarra EMEP desde la serie cruda; generada también para Valencia Vivers pero su tabla no se ha revisado en este informe todavía.
- Chequeo de pico semanal en h=7/14/21: sin pico dominante en ninguna de las dos series verificadas.
- Script canónico `scripts/01_generate_e1_rr_lags_only_predictions.py` inspeccionado por línea: confirma `HORIZONS = tuple(range(1,8))`, generación de filas de persistencia dentro del mismo CSV, y merge de skill por `origin_date` + `date`.
- Auditoría de merge por claves en Valencia Vivers: conteos idénticos modelo↔persistencia en `hgb_direct` y `ridge_direct`, los 7 horizontes.
- Recalculo de skill_emp (MSE) con merge correcto: positivo y creciente con h en Valencia Vivers, contradice el resultado negativo de la ronda anterior.
- Contraste contra ficheros versionados del propio repo (`skill_summary_valencia_vivers.csv`, `skill_summary_zarra_emep.csv`): consistentes con el resultado corregido.
- Limitación de procedencia: `git clone` a GitHub falló por proxy (403); se trabajó contra una copia local ya presente (`/workspace/varret-pm10-paper`), no verificada byte a byte contra `HEAD` remoto.

Ficheros generados por Codex (no accesibles desde esta sesión de Claude Code, solo referenciados aquí):
`/tmp/codex_hstar_audit/outputs/{theoretical,extended,empirical}_*.csv`, `weekly_rho_check.csv`, `audit_compute.py`.
