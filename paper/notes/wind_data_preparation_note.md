# Wind Data Preparation Note

For the wind domain, the preparation step maps the selected NREL Wind Toolkit series into a canonical hourly schema: `timestamp`, `value`.

The preprocessing contract enforces hourly regularity using `asfreq("h")`, removes duplicate timestamps, forward-fills missing values, and then drops any remaining missing rows.

This choice is a domain-specific preprocessing decision and should be stated explicitly when reporting wind-domain experiments (Methods and reproducibility sections).
