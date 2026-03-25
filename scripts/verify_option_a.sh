#!/usr/bin/env bash
set -u

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "ERROR: Este script debe ejecutarse dentro de un repositorio git."
  exit 2
}
cd "$ROOT" || exit 2

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass_count=0
fail_count=0

report() {
  local n="$1"
  local title="$2"
  local ok="$3"
  local detail="$4"

  if [[ "$ok" -eq 1 ]]; then
    pass_count=$((pass_count + 1))
    printf "%02d. PASS - %s\n" "$n" "$title"
    [[ -n "$detail" ]] && printf "    %s\n" "$detail"
  else
    fail_count=$((fail_count + 1))
    printf "%02d. FAIL - %s\n" "$n" "$title"
    [[ -n "$detail" ]] && printf "    %s\n" "$detail"
  fi
}

is_tracked() {
  git ls-files --error-unmatch "$1" >/dev/null 2>&1
}

rev_count() {
  git rev-list --all -- "$1" | wc -l | tr -d ' '
}

join_csv_lines() {
  paste -sd',' - | sed 's/,/, /g'
}

all_tracked() {
  local missing=()
  local p
  for p in "$@"; do
    if ! is_tracked "$p"; then
      missing+=("$p")
    fi
  done

  if [[ ${#missing[@]} -eq 0 ]]; then
    echo "OK"
    return 0
  fi

  printf "%s\n" "${missing[@]}"
  return 1
}

all_with_commits() {
  local missing=()
  local p c
  for p in "$@"; do
    c="$(rev_count "$p")"
    if [[ "$c" -lt 1 ]]; then
      missing+=("$p")
    fi
  done

  if [[ ${#missing[@]} -eq 0 ]]; then
    echo "OK"
    return 0
  fi

  printf "%s\n" "${missing[@]}"
  return 1
}

has_tracked_command_reference() {
  local regex="$1"
  git grep -I -n -E "$regex" HEAD -- . >/dev/null 2>&1
}

has_fallback_evidence() {
  local file
  while IFS= read -r file; do
    [[ -z "$file" ]] && continue

    if git show "HEAD:$file" | grep -Eqi 'traffic' \
      && git show "HEAD:$file" | grep -Eqi 'ARIMA' \
      && git show "HEAD:$file" | grep -Eqi 'fallback|did not complete|not practically runnable|runtime|timeout|too slow|no fue viable' \
      && git show "HEAD:$file" | grep -Eqi 'moving average|moving-average' \
      && git show "HEAD:$file" | grep -Eqi 'window\s*=\s*3|w=3'; then
      echo "$file"
      return 0
    fi
  done < <(git ls-tree -r --name-only HEAD | rg '\.(md|txt|tex|rst)$')

  return 1
}

wind_code=(
  "experiments/wind_arima_canonical_predictability.py"
)

wind_results=(
  "results/wind_arima_errors.csv"
  "results/wind_arima_skill.csv"
  "results/wind_arima_hstar.txt"
)

wind_figures=(
  "figures/wind_arima_error_vs_horizon.png"
  "figures/wind_arima_skill_vs_horizon.png"
)

traffic_code=(
  "experiments/traffic_arima_canonical_predictability.py"
)

traffic_results=(
  "results/traffic_arima_errors.csv"
  "results/traffic_arima_skill.csv"
  "results/traffic_arima_hstar.txt"
)

traffic_figures=(
  "figures/traffic_arima_error_vs_horizon.png"
  "figures/traffic_arima_skill_vs_horizon.png"
)

critical_paths=(
  "${wind_code[@]}"
  "${wind_results[@]}"
  "${wind_figures[@]}"
  "${traffic_code[@]}"
  "${traffic_results[@]}"
  "${traffic_figures[@]}"
)

# 1
if out="$(all_tracked "${wind_code[@]}" 2>/dev/null)"; then
  report 1 "wind-ARIMA código está versionado" 1 "${wind_code[*]}"
else
  report 1 "wind-ARIMA código está versionado" 0 "Faltan en git: $(echo "$out" | join_csv_lines)"
fi

# 2
if out="$(all_tracked "${wind_results[@]}" 2>/dev/null)"; then
  report 2 "wind-ARIMA resultados están versionados" 1 "${wind_results[*]}"
else
  report 2 "wind-ARIMA resultados están versionados" 0 "Faltan en git: $(echo "$out" | join_csv_lines)"
fi

# 3
if out="$(all_tracked "${wind_figures[@]}" 2>/dev/null)"; then
  report 3 "wind-ARIMA figuras están versionadas" 1 "${wind_figures[*]}"
else
  report 3 "wind-ARIMA figuras están versionadas" 0 "Faltan en git: $(echo "$out" | join_csv_lines)"
fi

# 4
if out="$(all_tracked "${traffic_code[@]}" 2>/dev/null)"; then
  report 4 "traffic-MA(w=3) código está versionado" 1 "${traffic_code[*]}"
else
  report 4 "traffic-MA(w=3) código está versionado" 0 "Faltan en git: $(echo "$out" | join_csv_lines)"
fi

# 5
if out="$(all_tracked "${traffic_results[@]}" 2>/dev/null)"; then
  report 5 "traffic-MA(w=3) resultados están versionados" 1 "${traffic_results[*]}"
else
  report 5 "traffic-MA(w=3) resultados están versionados" 0 "Faltan en git: $(echo "$out" | join_csv_lines)"
fi

# 6
if out="$(all_tracked "${traffic_figures[@]}" 2>/dev/null)"; then
  report 6 "traffic-MA(w=3) figuras están versionadas" 1 "${traffic_figures[*]}"
else
  report 6 "traffic-MA(w=3) figuras están versionadas" 0 "Faltan en git: $(echo "$out" | join_csv_lines)"
fi

# 7
if out="$(all_with_commits "${critical_paths[@]}" 2>/dev/null)"; then
  report 7 "cada artefacto nuevo tiene al menos 1 commit" 1 "Todas las rutas tienen trazabilidad histórica"
else
  report 7 "cada artefacto nuevo tiene al menos 1 commit" 0 "Sin commits para: $(echo "$out" | join_csv_lines)"
fi

# 8
cmd1='python3?[[:space:]]+experiments/wind_arima_canonical_predictability\.py'
cmd2='python3?[[:space:]]+experiments/traffic_arima_canonical_predictability\.py'
if has_tracked_command_reference "$cmd1" && has_tracked_command_reference "$cmd2"; then
  report 8 "hay instrucciones reproducibles con comandos explícitos para ambos scripts" 1 "Se detectan comandos en archivos versionados"
else
  detail=""
  if ! has_tracked_command_reference "$cmd1"; then
    detail+="No aparece comando para wind_arima_canonical_predictability.py en archivos versionados. "
  fi
  if ! has_tracked_command_reference "$cmd2"; then
    detail+="No aparece comando para traffic_arima_canonical_predictability.py en archivos versionados."
  fi
  report 8 "hay instrucciones reproducibles con comandos explícitos para ambos scripts" 0 "$detail"
fi

# 9
if fb_file="$(has_fallback_evidence 2>/dev/null)"; then
  report 9 "hay evidencia committeada del fallback traffic (ARIMA no viable -> MA w=3)" 1 "Archivo detectado: $fb_file"
else
  report 9 "hay evidencia committeada del fallback traffic (ARIMA no viable -> MA w=3)" 0 "No se encontró archivo versionado con traffic+ARIMA+fallback/runtime+moving average+window=3"
fi

# 10
paper_file="paper/paper2_draft.tex"
if git cat-file -e "HEAD:$paper_file" 2>/dev/null \
  && git show "HEAD:$paper_file" | grep -Eqi 'ARIMA\(2,0,0\)' \
  && git show "HEAD:$paper_file" | grep -Eqi 'Wind' \
  && git show "HEAD:$paper_file" | grep -Eqi 'Traffic' \
  && git show "HEAD:$paper_file" | grep -Eqi 'moving average|moving-average' \
  && git show "HEAD:$paper_file" | grep -Eqi 'window\s*=\s*3|w=3'; then
  report 10 "el manuscrito está alineado con los dos segundos modelos declarados" 1 "$paper_file contiene referencias de wind-ARIMA(2,0,0) y traffic-moving average (w=3)"
else
  report 10 "el manuscrito está alineado con los dos segundos modelos declarados" 0 "Revisar contenido de $paper_file (faltan referencias explícitas o archivo no trackeado)"
fi

# 11
untracked_critical=()
for p in "${critical_paths[@]}"; do
  if [[ "$(git status --porcelain -- "$p")" =~ ^\?\? ]]; then
    untracked_critical+=("$p")
  fi
done

if [[ ${#untracked_critical[@]} -eq 0 ]]; then
  report 11 "no quedan artefactos críticos UNTRACKED" 1 "Sin rutas críticas en estado ??"
else
  report 11 "no quedan artefactos críticos UNTRACKED" 0 "Aún UNTRACKED: $(printf '%s, ' "${untracked_critical[@]}" | sed 's/, $//')"
fi

# 12
if [[ "$fail_count" -eq 0 ]]; then
  report 12 "cierre editorial Opción A" 1 "Todos los checks pasan; se puede declarar respaldo committeado"
else
  report 12 "cierre editorial Opción A" 0 "Hay ${fail_count} checks en FAIL; todavía no cumple DoD"
fi

echo
echo "Resumen: PASS=${pass_count} FAIL=${fail_count}"

if [[ "$fail_count" -eq 0 ]]; then
  exit 0
else
  exit 1
fi
