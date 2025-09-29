import investpy
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
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
    lines.append("CALSCALE:GREGORIAN")
    
    for _, row in df.iterrows():
        lines.append("BEGIN:VEVENT")
        
        # ✅ Traitement des dates/heures
        if row["time"] and row["time"].lower() not in ["all day", "", "n/a", "tentative"]:
            try:
                # Parse la date + heure
                dt_naive = datetime.strptime(f"{row['date']} {row['time']}", "%d/%m/%Y %H:%M")
                
                # ✅ CORRECTION : investpy renvoie des heures locales de chaque pays
                # Pour simplifier, on considère que c'est l'heure de publication (souvent EST pour US, CET pour EUR)
                # On va localiser en Europe/Paris (car vous êtes en France)
                dt_local = dt_naive.replace(tzinfo=ZoneInfo("Europe/Paris"))
                
                # Convertir en UTC pour le fichier ICS
                dt_utc = dt_local.astimezone(ZoneInfo("UTC"))
                dt_ics = dt_utc.strftime("%Y%m%dT%H%M%SZ")
                
            except ValueError:
                # Si le parsing échoue, on met un événement "all day"
                dt_naive = datetime.strptime(row["date"], "%d/%m/%Y")
                dt_ics = dt_naive.strftime("%Y%m%d")
                lines.append(f"DTSTART;VALUE=DATE:{dt_ics}")
                lines.append(f"DTEND;VALUE=DATE:{dt_ics}")
        else:
            # Événement "all day"
            dt_naive = datetime.strptime(row["date"], "%d/%m/%Y")
            dt_ics = dt_naive.strftime("%Y%m%d")
            lines.append(f"DTSTART;VALUE=DATE:{dt_ics}")
            lines.append(f"DTEND;VALUE=DATE:{dt_ics}")
        
        # Si c'est un événement avec heure, on ajoute DTSTART normalement
        if row["time"] and row["time"].lower() not in ["all day", "", "n/a", "tentative"]:
            try:
                lines.append(f"DTSTART:{dt_ics}")
                # Durée de 30 minutes par défaut
                dt_end = dt_utc + timedelta(minutes=30)
                lines.append(f"DTEND:{dt_end.strftime('%Y%m%dT%H%M%SZ')}")
            except:
                pass
        
        # Résumé et description
        summary = f"📊 {row['currency']} - {row['event']}"
        lines.append(f"SUMMARY:{summary}")
        
        desc_parts = []
        if str(row['forecast']) != 'nan':
            desc_parts.append(f"Forecast: {row['forecast']}")
        if str(row['previous']) != 'nan':
            desc_parts.append(f"Previous: {row['previous']}")
        if str(row['actual']) != 'nan':
            desc_parts.append(f"Actual: {row['actual']}")
        
        desc = " | ".join(desc_parts) if desc_parts else "Economic event"
        lines.append(f"DESCRIPTION:{desc}")
        
        # ✅ UID stable basé sur les données de l'événement
        uid_seed = f"{row['date']}_{row['time']}_{row['currency']}_{row['event']}"
        uid_hash = hashlib.md5(uid_seed.encode()).hexdigest()
        lines.append(f"UID:{uid_hash}@financial-calendar.local")
        
        # Timestamp de création (optionnel mais recommandé)
        dtstamp = datetime.now(ZoneInfo("UTC")).strftime("%Y%m%dT%H%M%SZ")
        lines.append(f"DTSTAMP:{dtstamp}")
        
        lines.append("END:VEVENT")
    
    lines.append("END:VCALENDAR")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"✅ ICS généré : {OUTPUT_FILE} ({len(df)} événements)")

# --- Main ---
if __name__ == "__main__":
    # Date de référence
    today = datetime.now()
    next_week = today + timedelta(days=DAYS_AHEAD)
    
    print(f"🔍 Recherche d'événements du {today.strftime('%d/%m/%Y')} au {next_week.strftime('%d/%m/%Y')}")
    
    df_events = fetch_events(today, next_week)
    
    if df_events.empty:
        print("⚠️  Aucun événement à haute importance trouvé.")
    else:
        print(f"📅 {len(df_events)} événements trouvés")
        generate_ics(df_events)
