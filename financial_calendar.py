import investpy
from datetime import datetime, timedelta
import os

OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "financial_calendar.ics")
DAYS_AHEAD = 7
TIME_SHIFT_HOURS = 0  # <-- soustraction de 3 heures

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Récupération des événements ---
def fetch_events(start_date, end_date):
    df = investpy.economic_calendar(
        from_date=start_date.strftime("%d/%m/%Y"),
        to_date=end_date.strftime("%d/%m/%Y")
    )
    # filtrer uniquement les événements à haute importance
    df = df[df["importance"].str.lower() == "high"]
    return df

# --- Génération du fichier ICS (donnée brute) ---
def generate_ics(df):
    lines = []
    lines.append("BEGIN:VCALENDAR")
    lines.append("VERSION:2.0")
    lines.append("PRODID:-//Financial Calendar//EN")

    for _, row in df.iterrows():
        lines.append("BEGIN:VEVENT")

        # Date + heure telles que fournies par investpy
        if row["time"] and row["time"].lower() != "all day":
            dt = datetime.strptime(f"{row['date']} {row['time']}", "%d/%m/%Y %H:%M")
        else:
            dt = datetime.strptime(row["date"], "%d/%m/%Y")

        # --- Application du décalage de 3 heures ---
        dt_shifted = dt + timedelta(hours=TIME_SHIFT_HOURS)

        dt_ics = dt_shifted.strftime("%Y%m%dT%H%M%SZ")
        lines.append(f"DTSTART:{dt_ics}")

        # Résumé et description avec les mêmes noms que la DataFrame
        summary = f"{row['currency']} - {row['event']}"
        lines.append(f"SUMMARY:{summary}")

        desc = f"Forecast: {row['forecast']}, Previous: {row['previous']}, Actual: {row['actual']}"
        lines.append(f"DESCRIPTION:{desc}")

        lines.append(f"UID:{os.urandom(8).hex()}@fin.org")
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ ICS généré : {OUTPUT_FILE}")

# --- Main ---
if __name__ == "__main__":
    today = datetime.today()
    next_week = today + timedelta(days=DAYS_AHEAD)
    df_events = fetch_events(today, next_week)

    if df_events.empty:
        print("⚠ Aucun événement trouvé.")
    else:
        generate_ics(df_events)




