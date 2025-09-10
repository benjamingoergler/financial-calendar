import investpy
import pandas as pd
from ics import Calendar, Event
from datetime import datetime, timedelta
import arrow

# === CONFIGURATION ===
TIMEZONE = "Europe/Paris"  # Heure locale
OUTPUT_FILE = "financial_calendar.ics"
DAYS_AHEAD = 7  # récupérer une semaine à l'avance
FIXED_OFFSET_HOURS = -3  # Décalage fixe pour corriger le décalage observé

# === FONCTIONS ===
def fetch_events(start_date, end_date):
    """
    Récupère les événements économiques Investpy et filtre sur importance 'high'.
    """
    df = investpy.economic_calendar(
        from_date=start_date.strftime("%d/%m/%Y"),
        to_date=end_date.strftime("%d/%m/%Y")
    )
    df = df[df["importance"].str.lower() == "high"]
    return df

def generate_ics(df):
    """
    Crée un fichier ICS à partir des événements filtrés avec timezone correcte
    et applique un décalage fixe pour Paris.
    """
    cal = Calendar()

    for _, row in df.iterrows():
        e = Event()
        if row["time"] and row["time"].lower() != "all day":
            dt_str = f"{row['date']} {row['time']}"
            # Arrow pour gérer la date et l'heure
            dt = arrow.get(dt_str, "DD/MM/YYYY HH:mm")
            # Appliquer le décalage fixe
            dt = dt.shift(hours=FIXED_OFFSET_HOURS)
            e.begin = dt
        else:
            dt = arrow.get(row["date"], "DD/MM/YYYY").shift(hours=FIXED_OFFSET_HOURS)
            e.begin = dt

        # Nom de l'événement avec le pays
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

    print(f"Récupération des événements économiques du {today.strftime('%d/%m/%Y')} au {next_week.strftime('%d/%m/%Y')}...")
    df_events = fetch_events(today, next_week)

    if df_events.empty:
        print("⚠ Aucun événement 3 étoiles trouvé pour la période demandée.")
    else:
        print(f"{len(df_events)} événements 3 étoiles récupérés.")
        generate_ics(df_events)
