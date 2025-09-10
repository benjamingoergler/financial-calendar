import investpy
import pandas as pd
from ics import Calendar, Event
from datetime import datetime, timedelta
import arrow
import pytz
import os

# === CONFIGURATION ===
OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "financial_calendar.ics")
DAYS_AHEAD = 7
TIMEZONE = "Europe/Paris"  # fuseau horaire pour tous les événements

# Crée le dossier output si inexistant
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === FONCTIONS ===
def fetch_events(start_date, end_date):
    df = investpy.economic_calendar(
        from_date=start_date.strftime("%d/%m/%Y"),
        to_date=end_date.strftime("%d/%m/%Y")
    )
    # Ne garder que les événements à haute importance
    df = df[df["importance"].str.lower() == "high"]
    return df

def generate_ics(df):
    cal = Calendar()
    tz = pytz.timezone(TIMEZONE)

    for _, row in df.iterrows():
        e = Event()
        # Gestion de l'heure
        if row["time"] and row["time"].lower() != "all day":
            dt_str = f"{row['date']} {row['time']}"
            dt = arrow.get(dt_str, "DD/MM/YYYY HH:mm").datetime
            dt = tz.localize(dt)  # applique le fuseau horaire Europe/Paris
            e.begin = dt
        else:
            dt = arrow.get(row["date"], "DD/MM/YYYY").datetime
            dt = tz.localize(dt)
            e.begin = dt

        # Titre et description
        e.name = f"{row['currency']} - {row['event']}"
        e.description = f"Forecast: {row['forecast']}, Previous: {row['previous']}, Actual: {row['actual']}"

        cal.events.add(e)

    # Sauvegarde du fichier ICS
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
