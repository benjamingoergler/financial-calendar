import investpy
from ics import Calendar, Event
from datetime import datetime, timedelta

# === CONFIG ===
OUTPUT_FILE = "financial_calendar.ics"  # même nom qu'avant
DAYS_AHEAD = 7

# === FONCTIONS ===
def fetch_events(start_date, end_date):
    df = investpy.economic_calendar(
        from_date=start_date.strftime("%d/%m/%Y"),
        to_date=end_date.strftime("%d/%m/%Y")
    )
    df = df[df["importance"].str.lower() == "high"]
    return df

def generate_raw_ics(df):
    cal = Calendar()
    for _, row in df.iterrows():
        e = Event()
        # On prend directement la date/heure telle quelle, sans conversion
        if row["time"] and row["time"].lower() != "all day":
            dt_str = f"{row['date']} {row['time']}"
            dt = datetime.strptime(dt_str, "%d/%m/%Y %H:%M")
        else:
            dt = datetime.strptime(row['date'], "%d/%m/%Y")
        e.begin = dt
        e.name = f"{row['currency']} - {row['event']}"
        e.description = f"Forecast: {row['forecast']}, Previous: {row['previous']}, Actual: {row['actual']}"
        cal.events.add(e)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.writelines(cal)
    print(f"✅ ICS brut généré : {OUTPUT_FILE}")

# === EXECUTION ===
if __name__ == "__main__":
    today = datetime.today()
    next_week = today + timedelta(days=DAYS_AHEAD)
    df_events = fetch_events(today, next_week)

    if df_events.empty:
        print("⚠ Aucun événement 3 étoiles trouvé.")
    else:
        generate_raw_ics(df_events)
