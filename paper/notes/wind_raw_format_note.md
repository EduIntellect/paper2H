# Wind Raw Format Note

The real NREL Wind Toolkit raw file required a domain-specific parser because the downloaded CSV includes a metadata line and separate temporal columns (`Year`, `Month`, `Day`, `Hour`, `Minute`), together with the wind variable `wind speed at 100m (m/s)`.

The preprocessing step converts this raw structure into the canonical hourly schema (`timestamp`, `value`), which is then used for reproducible forecasting experiments.
