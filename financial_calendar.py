import investpy
import pandas as pd
from ics import Calendar, Event
from datetime import datetime, timedelta
import arrow
import pytz

# === CONFIGURATION ===
OUTPUT_FILE = "output/financial_calendar.ics"
DAYS_AHEAD = 7
TIMEZONE = "Europe/Paris"  # fuseau horaire fixe

# === FONCTIONS ===
def fetch_events(start_date, end_date):
    df = investpy.economic_calendar(
        from_date=start_date.strftime("%d/%m/%Y"),
        to_date=end_date.strftime("%d/%m/%Y")
    )
    df = df[df["importance"].str.lower() == "high"]
    return df

def generate_ics(df):
    tz = pytz.timezone(TIMEZONE)
    cal = Calendar()

    for _, row in df.iterrows():
        e = Event()
        if row["time"] and row["time"].lower() != "all day":
            dt_str = f"{row['date']} {row['time']}"
            dt = arrow.get(dt_str, "DD/MM/YYYY HH:mm").datetime
            dt = dt.replace(tzinfo=None)  # s'assure que datetime est naïf
            dt = tz.localize(dt)
            e.begin = dt
        else:
            dt = arrow.get(row["date"], "DD/MM/YYYY").datetime
            dt = dt.replace(tzinfo=None)
            dt = tz.localize(dt)
            e.begin = dt

        e.name = f"{row['currency']} - {row['event']}"
        e.description = f"Forecast: {row['forecast']}, Previous: {row['previous']}, Actual: {row['actual']}"
        cal.events.add(e)

    # Section VTIMEZONE complète
    vtimezone = f"""BEGIN:VTIMEZONE
TZID:{TIMEZONE}
BEGIN:STANDARD
DTSTART:19700101T000000
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
TZNAME:CET
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19700101T000000
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
TZNAME:CEST
END:DAYLIGHT
END:VTIMEZONE
"""

    # Écriture manuelle dans le fichier ICS pour éviter l'erreur clone
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:ics.py - http://git.io/lLljaA\n")
        f.write(vtimezone + "\n")
        for event in cal.events:
            f.write(event.serialize() + "\n")
        f.write("END:VCALENDAR\n")

    print(f"✅ ICS généré avec fuseau complet : {OUTPUT_FILE}")

# === EXECUTION ===
if __name__ == "__main__":
    today = datetime.today()
    next_week = today + timedelta(days=DAYS_AHEAD)
    df_events = fetch_events(today, next_week)

    if df_events.empty:
        print("⚠ Aucun événement 3 étoiles trouvé.")
    else:
        generate_ics(df_events)
