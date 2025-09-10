import investpy
from datetime import datetime, timedelta
import os

OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "financial_calendar.ics")
DAYS_AHEAD = 7

os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_events(start_date, end_date):
    df = investpy.economic_calendar(
        from_date=start_date.strftime("%d/%m/%Y"),
        to_date=end_date.strftime("%d/%m/%Y")
    )
    df = df[df["importance"].str.lower() == "high"]  # seulement importance haute
    return df

def generate_ics(df):
    lines = []
    lines.append("BEGIN:VCALENDAR")
    lines.append("VERSION:2.0")
    lines.append("PRODID:-//Financial Calendar//EN")

    for _, row in df.iterrows():
        lines.append("BEGIN:VEVENT")

        if row["time"] and row["time"].lower() != "all day":
            dt_str = f"{row['date']} {row['time']}"
            dt = datetime.strptime(dt_str, "%d/%m/%Y %H:%M")
            # 🔥 appliquer -2 heures
            dt = dt - timedelta(hours=2)
            dt_ics = dt.strftime("%Y%m%dT%H%M%SZ")
        else:
            dt = datetime.strptime(row["date"], "%d/%m/%Y")
            dt = dt - timedelta(hours=2)
            dt_ics = dt.strftime("%Y%m%dT%H%M%SZ")

        lines.append(f"DTSTART:{dt_ics}")
        lines.append(f"SUMMARY:{row['currency']} - {row['event']}")
        desc = f"Forecast: {row['forecast']}, Previous: {row['previous']}, Actual: {row['actual']}"
        lines.append(f"DESCRIPTION:{desc}")
        lines.append(f"UID:{os.urandom(8).hex()}@fin.org")
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ ICS généré : {OUTPUT_FILE}")

if __name__ == "__main__":
    today = datetime.today()
    next_week = today + timedelta(days=DAYS_AHEAD)
    df_events = fetch_events(today, next_week)

    if df_events.empty:
        print("⚠ Aucun événement trouvé.")
    else:
        generate_ics(df_events)
