import investpy
import pandas as pd
from ics import Calendar, Event
from datetime import datetime, timedelta
import arrow

# === CONFIGURATION ===
OUTPUT_FILE = "financial_calendar.ics"
DAYS_AHEAD = 7
FIXED_OFFSET_HOURS = 2  # +2 heures pour corriger le décalage

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
            dt = arrow.get(dt_str, "DD/MM/YYYY HH:mm").shift(hours=FIXED_OFFSET_HOURS)
        else:
            dt = arrow.get(row["date"], "DD/MM/YYYY").shift(hours=FIXED_OFFSET_HOURS)
        
        # Mettre en UTC pour Google Calendar
        e.begin = dt.to("UTC")
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
