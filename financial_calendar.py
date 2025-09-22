import investpy
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # Python 3.9+
import os
import hashlib

OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "financial_calendar.ics")
DAYS_AHEAD = 14

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Récupération des événements ---
def fetch_events(start_date, end_date):
    df = investpy.economic_calendar(
        from_date=start_date.strftime("%d/%m/%Y"),
        to_date=end_date.strftime("%d/%m/%Y")
    )
    # Filtrer uniquement les événements à haute importance
    df = df[df["importance"].str.lower() == "high"]
    return df

# --- Génération du fichier ICS (stable) ---
def generate_ics(df):
    lines = []
    lines.append("BEGIN:VCALENDAR")
    lines.append("VERSION:2.0")
    lines.append("PRODID:-//Financial Calendar//EN")
    
    for _, row in df.iterrows():
        lines.append("BEGIN:VEVENT")
        
        # ✅ Traitement uniforme des dates/heures
        if row["time"] and row["time"].lower() not in ["all day", "", "n/a"]:
            # Cas avec heure spécifique
            dt = datetime.strptime(f"{row['date']} {row['time']}", "%d/%m/%Y %H:%M")
        else:
            # Cas "all day" - on met à 12h00 par défaut
            dt = datetime.strptime(row["date"], "%d/%m/%Y").replace(hour=12, minute=0)
        
        # ✅ Les données investpy sont généralement en UTC ou EST
        # On assume UTC et on convertit proprement
        dt_utc = dt.replace(tzinfo=ZoneInfo("UTC"))
        
        # ✅ Pour avoir l'heure locale française, on ajoute 1h (ou 2h en été)
        # Mais pour l'ICS, on reste en UTC
        dt_ics = dt_utc.strftime("%Y%m%dT%H%M%SZ")
        
        lines.append(f"DTSTART:{dt_ics}")
        
        # Résumé et description
        summary = f"{row['currency']} - {row['event']}"
        lines.append(f"SUMMARY:{summary}")
        
        desc = f"Forecast: {row['forecast']}, Previous: {row['previous']}, Actual: {row['actual']}"
        lines.append(f"DESCRIPTION:{desc}")
        
        # ✅ UID stable basé sur les données de l'événement
        uid_seed = f"{row['date']}_{row['time']}_{row['currency']}_{row['event']}"
        uid_hash = hashlib.md5(uid_seed.encode()).hexdigest()
        lines.append(f"UID:{uid_hash}@fin.org")
        
        lines.append("END:VEVENT")
    
    lines.append("END:VCALENDAR")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"✅ ICS généré : {OUTPUT_FILE}")

# --- Main ---
if __name__ == "__main__":
    # Date de référence en timezone locale
    today = datetime.now(tz=ZoneInfo("Europe/Paris")).replace(tzinfo=None)
    next_week = today + timedelta(days=DAYS_AHEAD)
    
    df_events = fetch_events(today, next_week)
    
    if df_events.empty:
        print("⚠ Aucun événement trouvé.")
    else:
        print(f"📅 {len(df_events)} événements trouvés")
        generate_ics(df_events)
