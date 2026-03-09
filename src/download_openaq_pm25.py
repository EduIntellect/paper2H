import requests
import pandas as pd

url = "https://api.openaq.org/v2/measurements"

params = {
    "parameter": "pm25",
    "limit": 1000,
    "sort": "desc",
}

r = requests.get(url, params=params)

data = r.json()

if "results" not in data:
    print("API response:")
    print(data)
    raise Exception("OpenAQ API did not return 'results'")

records = []

for d in data["results"]:
    records.append({
        "timestamp": d["date"]["utc"],
        "PM25": d["value"]
    })

df = pd.DataFrame(records)

df = df.sort_values("timestamp")

df.to_csv("data/pm25_series.csv", index=False)

print("Saved data/pm25_series.csv")
print("Rows:", len(df))
