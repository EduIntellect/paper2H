# Auditoría remota H* / censura / cota teórica — organización `fedeg-umh-es`

**ROJO (estructural, por bloqueo de acceso) — con una excepción ÁMBAR parcial no verificada de forma independiente**

> Este ROJO **no** significa "se confirmó ausencia de datos". Significa: de los 16 repos de la organización, 15 quedaron **sin inspeccionar** por un bloqueo de plataforma (no de permisos de GitHub), y el único con evidencia disponible (`varret-pm10-paper`) llega de **segunda mano** — un análisis que tú ejecutaste en otra sesión/entorno, no verificado directamente por esta sesión contra el repo remoto. Ver §0 y §6.

---

## 0. Qué pudo hacerse y qué no

Esta sesión de Claude Code está anclada al owner `eduintellect` (fuente `eduintellect/paper2h`). El servidor MCP de GitHub de esta sesión permite `search_repositories` (búsqueda global) pero **deniega** `get_file_contents`, `list_branches`, `list_commits`, etc. sobre cualquier repo no "configurado" en la sesión, y `add_repo` rechazó explícitamente los 16 repos de `fedeg-umh-es`:

```
add_repo: cross-tier adds are not supported in v1: requested "fedeg-umh-es/<repo>"
but session already has repos from owner(s) [eduintellect]. Start a new session
with the requested repo as the initial source...
```

No existe en esta sesión una herramienta para crear sesiones nuevas ni `gh` CLI. Por tanto:

- **Fase 0 (descubrimiento)**: completa. 16 repos confirmados vía `search_repositories` (metadata: nombre, descripción, visibilidad, fecha de push). Ver tabla §1.
- **Fase 1 (datos) y Fase 2 (código)**: **bloqueadas** para 15/16 repos — cero acceso a árboles, ficheros o contenido.
- **Excepción**: aportaste un volcado de resultados de un script (`test_cota_teorica_skill.py`) ejecutado fuera de esta sesión sobre tres series PM10 (Elche, Valencia Vivers, Zarra EMEP). Preguntado el origen, respondiste "decídelo tú". Por coincidencia de nombre/descripción del repo (único en la org que menciona explícitamente "rolling-origin", "diagnostic skill adjustment" y "multi-horizon PM10 forecasting") atribuyo esta evidencia, **sin confirmación directa**, a `fedeg-umh-es/varret-pm10-paper`. Esta atribución debe verificarse en cuanto haya acceso real.
- Los ficheros que citas (`data/raw/pm10_daily.csv`, `outputs/metrics/predictions*.csv`, `test_cota_teorica_skill.py`) **no existen** en este repo de trabajo (`paper2h`), que tiene su propia estructura (`data/pm10_elx_daily.csv`, `results/hstar_all_domains.csv`, etc.) y pertenece a otro owner — se ha excluido de la evidencia de organización según la regla central del encargo.

---

## 1. Fase 0 — Inventario (16 repos, metadata únicamente)

| Repo | Último push | Visibilidad | Motivo de inclusión | Prioridad |
|---|---|---|---|---|
| varret-pm10-paper | 2026-06-04 | público | pm10, rolling-origin, skill, "diagnostic" | Alta |
| PM10-Horizons-Diagnostic | 2026-04-15 | internal | pm10, horizon | Alta |
| madrid-pm10-rank-reversal | 2026-04-14 | internal | pm10 | Alta |
| Hstar_PM10_PM25_Madrid_Valencia | 2026-04-28 | público | hstar, pm10, pm25 | Alta |
| P32_IJF_GhostSkill_Hstar | 2026-04-27 | público | skill, hstar | Alta |
| P1_PM10_Meteorology_Hstar | 2026-05-29 | internal | pm10, hstar | Alta |
| hstar | 2026-04-01 | internal | hstar | Alta |
| hstar-p3-prob-operational-probabilistic-predictability | 2026-04-11 | internal | hstar, predictability | Alta |
| P33_variance_collapse | 2026-04-17 | público | variance (skill-adyacente) | Media |
| P34_forecasting_library | 2026-04-17 | público | forecast (librería) | Media |
| p34-variance-retention-api | 2026-05-14 | público | variance-retention (API) | Media |
| paper_c_kge_variance | 2026-05-04 | público | variance, kge (métrica) | Media |
| e2-met-validation | 2026-04-13 | internal | descripción menciona "PM10 Madrid 2015-2024" | Media |
| GB-style | 2026-05-31 | público | sin coincidencia de keywords | Baja — sin señal, no auditable |
| ltw | 2026-04-18 | público | sin coincidencia de keywords (lenguaje C) | Baja — sin señal, no auditable |
| Code2_AI | 2026-03-28 | internal | sin coincidencia de keywords | Baja — sin señal, no auditable |

Ningún repo pudo abrirse (árbol, README, código, datos) desde esta sesión. La columna "Prioridad" refleja únicamente nombre/descripción, no contenido verificado.

---

## 2. Fase 1 y Fase 2 — Datos y código

**No ejecutables** para 15/16 repos: bloqueo de scope de sesión (§0). Ninguna tabla de ficheros, columnas o patrones de código puede rellenarse con evidencia propia para estos repos.

Para `varret-pm10-paper` (atribución no confirmada), la evidencia de segunda mano indica:

| Ruta reportada | Tipo | Observación |
|---|---|---|
| `data/raw/pm10_daily.csv` | serie cruda | Elche, n=2350, usada por el script para ACF/AR(1) |
| `data/raw/pm10_valencia_vivers.csv` | serie cruda | Valencia Vivers, n=2679 |
| `data/raw/pm10_zarra_emep.csv` | serie cruda | Zarra EMEP, n=2804 |
| `outputs/metrics/predictions.csv` | predicciones | columna `model`, incluye filas `model == "persistence"`; **sin** columna `baseline` nativa |
| `outputs/metrics/predictions_valencia_vivers.csv` | predicciones | ídem |
| `outputs/metrics/predictions_zarra_emep.csv` | predicciones | ídem |

Nota metodológica importante que tú mismo señalas: al no existir columna `baseline` separada, tuviste que generar CSV temporales en `/tmp` reconstruyéndola a partir de las filas `model == "persistence"`, **sin tocar la lógica del script**. Esto es una reconstrucción manual válida para el propósito de la prueba, pero implica que **el formato nativo del repo no trae la comparación model-vs-persistence lista para usar** — es un dato a favor de ÁMBAR (recomputable sin reentrenar) y en contra de VERDE (no está "listo en disco" tal cual).

No hay evidencia (ni de primera ni de segunda mano) de `fold_id`/`origin` ni de ficheros de partición train/test explícitos. El nombre del repo sugiere "rolling-origin evaluation", pero esto **no está verificado**.

---

## 3. Fase 3 — Cruce de evidencia

**1. ¿Existe skill_h por fold y horizonte en disco remoto?**
No determinable en 15/16 repos (bloqueo de acceso). En `varret-pm10-paper` (atribución no confirmada): **parcial** — hay granularidad por horizonte `h` (1–7) reconstruida por el script; no hay evidencia de granularidad por `fold_id`/`origin`.

**2. ¿Cuál es Hmax por dominio?**
Solo conocido para las 3 series reportadas: Hmax = 7 (días) en Elche, Valencia Vivers y Zarra EMEP. No documentado si es un límite hardcodeado del script de prueba (creado ad hoc para esta comprobación) o del pipeline original del repo — dato pendiente de verificar in situ.

**3. ¿Se puede saber si skill(Hmax) > 0 en cada fold sin reentrenar?**
Sí, a nivel agregado (no por fold) para las 3 series, usando el script ya ejecutado:
- Elche: skill_emp(h=7) = **0.444 > 0**
- Valencia Vivers: skill_emp(h=7) = **-0.365 < 0**
- Zarra EMEP: skill_emp(h=7) = **0.099 > 0**
Sin desglose por fold, no se puede afirmar que esto se cumpla en *cada* fold individualmente — solo en el agregado reportado.

**4. ¿Cuántos dominios tienen perfil completo (skill por fold y horizonte)?**
**Cero** confirmados. Las 3 series de `varret-pm10-paper` tienen perfil por horizonte pero no por fold (no verificado).

**5. ¿Hay predicciones crudas y_true/y_pred por fold y horizonte?**
No determinable en 15/16 repos. En las 3 series reportadas: hay predicciones por horizonte con etiqueta de modelo (incluida persistencia), suficientes para derivar MSE por horizonte tras reconstrucción manual de la columna baseline. No confirmado que sean y_true/y_pred crudos vs. errores ya agregados, ni que existan por fold.

**6. ¿Está disponible la serie objetivo cruda con índice temporal y los rangos train/test por fold?**
Serie cruda: **sí**, confirmada por ejecución exitosa del script (usa la serie para calcular ACF) en las 3 estaciones de `varret-pm10-paper`. Rangos train/test por fold: **no confirmados** — no reportados por el usuario ni verificables por esta sesión.

**7. [Extra] ¿Algún repo de la organización contiene los perfiles multidominio (Pekín PM2.5, eólica, tráfico) o solo PM10?**
**No confirmado en ningún repo de `fedeg-umh-es`.** De los 16 nombres/descripciones, todos son PM10-céntricos salvo posibles excepciones genéricas sin confirmar (`P34_forecasting_library`, librería sin descripción; `paper_c_kge_variance`, métrica KGE típica de hidrología, no necesariamente aire). El multidominio (PM2.5 Pekín, eólica, tráfico, carga eléctrica) **vive en `eduintellect/paper2h`** — el repo de trabajo de esta sesión, confirmado con `results/pm25_skill_all.csv`, `results/wind_skill_all.csv`, `results/traffic_skill_all.csv`, `results/hstar_all_domains.csv` — pero ese repo pertenece a otro owner y queda **fuera del alcance de esta auditoría organizacional** por la regla central del encargo. Se registra como `missing_item` crítico.

**8. [Extra] ¿Existe `benchmark-pm-hstar` renombrado (heredado por `P34_forecasting_library` o `hstar`)?**
**No determinable.** Bloqueo de acceso impide leer READMEs, `git log --follow` o metadata de renombrado de ambos repos desde esta sesión.

---

## 4. Interpretación de la evidencia de segunda mano (con reservas)

Sobre los datos que tú ejecutaste y pegaste (no verificados independientemente por esta sesión):

- **Elche**: skill_emp sigue de cerca la cota ACF en todo el rango (gap entre -0.004 y -0.052) y **sigue positivo y sin señal de cruce a cero en h=7** (0.444, tras pico de 0.461 en h=5). Esto **es compatible con censura por la derecha**: nada en el perfil sugiere que el skill vaya a cero cerca de Hmax=7; extender el horizonte parece necesario para localizar el verdadero H*.
- **Zarra EMEP**: skill_emp cruza de negativo a positivo entre h=3 (-0.315) y h=4 (+0.015), y permanece positivo hasta h=7 (0.099) pero muy por debajo de la cota ACF (gap ≈ -0.37/-0.38). También compatible con censura por la derecha, aunque el margen sobre cero en h=4–7 es pequeño y **no se reportan intervalos de confianza** — no se puede descartar que sea ruido.
- **Valencia Vivers**: skill_emp es **negativo en todo el rango** (-1.582 a -0.365), muy por debajo tanto de la cota AR1 como de la ACF. Esto no es evidencia de censura por la derecha — es una señal de que el modelo evaluado se comporta sistemáticamente peor que la persistencia, lo que apunta a un problema de comparabilidad (escala, alineación temporal model/baseline, o la serie no siendo AR(1) puro, como bien señala tu propio veredicto). **Antes de interpretar H* en esta serie hace falta revisión metodológica, no solo cota teórica.**
- La búsqueda de periodicidad semanal (rho(7) vs. rho(6)/rho(8)) no encontró un pico dominante en ninguna de las 3 series, lo que descarta la estacionalidad semanal como explicación alternativa del patrón — dato limpio y bien acotado, sin reservas.

**Limitación estructural de este bloque**: todo lo anterior depende de un script y unos CSV auxiliares (columna `baseline` reconstruida en `/tmp`) que esta sesión no ha visto ni ejecutado. No hay forma de auditar aquí si la reconstrucción de la columna `baseline` preservó la alineación fila-a-fila correcta entre predicciones del modelo y de persistencia.

---

## 5. Qué falta, por coste ascendente

**(i) Recomputable en minutos** (una vez haya acceso real al repo):
- Confirmar el esquema exacto de `outputs/metrics/predictions*.csv` (columnas, si `model=="persistence"` está alineado por fila con las predicciones del modelo).
- Confirmar si existe `fold_id`/`origin` en algún fichero no listado por el usuario.
- Revisar por qué Valencia Vivers y Zarra EMEP dan skill_emp fuertemente negativo en horizontes cortos (posible bug de escala/alineación).

**(ii) Requiere descargar/inspeccionar datos** (bloqueado hasta nueva sesión con owner `fedeg-umh-es`):
- Fase 0-2 completas para los 15 repos restantes.
- Verificar la atribución de la evidencia aportada (¿es realmente `varret-pm10-paper`?).
- Buscar particiones train/test explícitas y `Hmax` documentado (vs. hardcodeado en un script ad hoc).
- Resolver preguntas 7 y 8.

**(iii) Requiere reentrenar**: ninguno identificado todavía — si se confirma fold_id y baseline alineado, la censura parece recomputable sin reentrenar.

---

## 6. Tabla de disponibilidad

| Dominio | Repo (atribución) | Fichero | Hmax | skill(fold,h) | y_true/y_pred | Serie cruda | Particiones | Censura detectable |
|---|---|---|---|---|---|---|---|---|
| Elche (PM10) | varret-pm10-paper* | predictions.csv + pm10_daily.csv | 7 | No (solo por h) | Parcial | Sí | No confirmado | **Sí — compatible** |
| Valencia Vivers (PM10) | varret-pm10-paper* | predictions_valencia_vivers.csv + pm10_valencia_vivers.csv | 7 | No (solo por h) | Parcial | Sí | No confirmado | No aplica — skill negativo, revisar metodología |
| Zarra EMEP (PM10) | varret-pm10-paper* | predictions_zarra_emep.csv + pm10_zarra_emep.csv | 7 | No (solo por h) | Parcial | Sí | No confirmado | **Sí — compatible, margen pequeño** |
| 15 repos restantes | fedeg-umh-es/* | — | — | No determinable | No determinable | No determinable | No determinable | No determinable — bloqueo de acceso |

\* Atribución no confirmada directamente por esta sesión; asignada por coincidencia de descripción tras indicación explícita del usuario ("decídelo tú").

---

## 7. Veredicto final

**ROJO estructural.** No por evidencia de que los datos no existan, sino porque **15 de 16 repos no pudieron inspeccionarse** desde esta sesión, y el único fragmento de evidencia disponible sobre el 16º es de segunda mano y con atribución no confirmada. La censura por la derecha en H* parece **compatible** en 2 de las 3 series reportadas (Elche, Zarra EMEP) pero esto no constituye una auditoría de organización — es, en el mejor de los casos, una pista a seguir con acceso real.

**Acción mínima para desbloquear**: abrir una sesión de Claude Code con un repo de `fedeg-umh-es` como fuente inicial y repetir Fases 0-2 con acceso real, o correr `gh` autenticado en un entorno sin esta restricción de scope.
