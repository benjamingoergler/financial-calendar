import investpy
import pandas as pd
from ics import Calendar, Event
from datetime import datetime, timedelta
import arrow
import pytz

# === CONFIGURATION ===
OUTPUT_FILE = "financial_calendar.ics"
DAYS_AHEAD = 7
TIMEZONE = "Europe/Paris"

# Fuseau horaire Paris
paris_tz = pytz.timezone(TIMEZONE)

# === FONCTIONS ===
def get_utc_offset_hours(date):
    """
    Retourne le décalage UTC en heures pour Paris à une date donnée
    (1h en hiver, 2h en été).
    """
    return int(paris_tz.utcoffset(date).total_seconds() / 3600)

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
            dt = arrow.get(dt_str, "DD/MM/YYYY HH:mm").datetime
            offset = get_utc_offset_hours(dt)
            dt = dt + timedelta(hours=offset)
            e.begin = dt
        else:
            dt = arrow.get(row["date"], "DD/MM/YYYY").datetime
            offset = get_utc_offset_hours(dt)
            dt = dt + timedelta(hours=offset)
            e.begin = dt

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
        print("⚠ Aucun événement 3 étoiles trouvé.")
    else:
        generate_ics(df_events)
