import investpy
import pandas as pd
from ics import Calendar, Event
from datetime import datetime, timedelta
import arrow

# === CONFIGURATION ===
OUTPUT_FILE = "financial_calendar.ics"
DAYS_AHEAD = 7
PARIS_TZ = "Europe/Paris"

# === FONCTIONS ===
def fetch_events(start_date, end_date):
    df = investpy.economic_calendar(
        from_date=start_date.strftime("%d/%m/%Y"),
        to_date=end_date.strftime("%d/%m/%Y")
    )
    df = df[df["importance"].str.lower() == "high"]
    return df

def generate_ics(df):
    cal = Calendar()

    for _, row in df.iterrows():
        e = Event()

        if row["time"] and row["time"].lower() != "all day":
            dt_str = f"{row['date']} {row['time']}"
            # datetime en Paris
            dt_paris = arrow.get(dt_str, "DD/MM/YYYY HH:mm", tzinfo=PARIS_TZ)
            # Convertir en UTC en ajoutant 1h de correction
            dt_utc = dt_paris.to("UTC").shift(hours=1)
            e.begin = dt_utc
        else:
            dt_paris = arrow.get(row["date"], "DD/MM/YYYY", tzinfo=PARIS_TZ)
            dt_utc = dt_paris.to("UTC").shift(hours=1)
            e.begin = dt_utc

        e.name = f"{row['currency']} - {row['event']}"
        e.description = f"Forecast: {row['forecast']}, Previous: {row['previous']}, Actual: {row['actual']}"
        cal.events.add(e)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.writelines(cal)

    print(f"✅ ICS généré : {OUTPUT_FILE}")

# === EXECUTION ===
if __name__ == "__main__":
    today = datetime.today()
    next_week = today + timedelta(days=DAYS_AHEAD)
    df_events = fetch_events(today, next_week)

    if df_events.empty:
        print("⚠ Aucun événement 3 étoiles trouvé pour la période demandée.")
    else:
        generate_ics(df_events)
