#!/usr/bin/env bash
# Run this yourself. It adds wind and traffic to the data cache, commits ONLY that folder,
# tags it and pushes. Review each step; stop with Ctrl+C if anything looks wrong.
set -euo pipefail
cd /home/fede/repos/paper2H

# 1. Copy the two missing inputs into release/ (data/ ignores them in Git; release/ does not).
cp data/wind_hourly_clean.csv data/traffic_hourly_clean.csv release/data_cache_four_domain/

# 2. Rebuild checksums and verify them against data/MANIFEST.tsv for wind and traffic.
cd release/data_cache_four_domain
sha256sum pm25_beijing_hourly_raw.csv load_uci_daily_aggregate.csv wind_hourly_clean.csv traffic_hourly_clean.csv > SHA256SUMS
sha256sum -c SHA256SUMS
grep -q 8f094e6437b50b5fd6837bfe43ad6f8a262bf5a9eec84472f2062eaac780a309 SHA256SUMS   # wind
grep -q 50fb3f411b7521cf72fc87e5660ce2809df67c9507619a6578d4d42e925d479c SHA256SUMS   # traffic
cd ../..

# 3. Commit only the cache folder (your other uncommitted changes stay out).
git status --short release/
git add release/data_cache_four_domain
git -c user.name="Federico García Crespí" -c user.email="fedeg@umh.es" commit -m "Add wind and traffic inputs to the data cache and document terms" -- release/data_cache_four_domain

# 4. Tag and push.
git -c user.name="Federico García Crespí" -c user.email="fedeg@umh.es" tag -a data-cache-v1 -m "Four-domain input cache for the DMKD revision"
git push origin main data-cache-v1

# 5. Check that the files are publicly reachable (expect 200 four times).
for f in pm25_beijing_hourly_raw.csv load_uci_daily_aggregate.csv wind_hourly_clean.csv traffic_hourly_clean.csv; do
  curl -s -o /dev/null -w "$f %{http_code}\n" \
    "https://raw.githubusercontent.com/EduIntellect/paper2H/data-cache-v1/release/data_cache_four_domain/$f"
done
echo "Citable URL: https://github.com/EduIntellect/paper2H/tree/data-cache-v1/release/data_cache_four_domain"
