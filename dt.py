import pandas as pd
import numpy as np
from datetime import datetime

# 1. Definizione dell'intervallo temporale (1 mese a intervalli orari)
start_date = datetime(2026, 7, 1)
end_date = datetime(2026, 7, 31, 23, 0)
date_range = pd.date_range(start=start_date, end=end_date, freq='h')

df = pd.DataFrame({'timestamp': date_range})
df['ora'] = df['timestamp'].dt.hour
df['giorno_settimana'] = df['timestamp'].dt.dayofweek  # 0 = Lunedì, 6 = Domenica

# 2. Configurazione dei parametri energetici
base_load = 1.2  # Consumo minimo costante in kW (es. server, standby)
picco_ufficio = 8.5  # Consumo medio durante le ore di lavoro in kW
potenza_fotovoltaico = 6.0  # Potenza massima dell'impianto solare in kW

# 3. Funzione per generare il consumo realistico
def calcola_consumo(row):
    ora = row['ora']
    giorno = row['giorno_settimana']
    
    # Se è weekend (Sabato=5, Domenica=6)
    if giorno >= 5:
        # Consumo ridotto al solo carico di base con un piccolo rumore casuale
        consumo = base_load + np.random.normal(0.2, 0.1)
    else:
        # Giorno lavorativo
        if 8 <= ora <= 18:
            # Ore di ufficio: picco di attività + rumore casuale
            consumo = base_load + picco_ufficio + np.random.normal(1.5, 0.7)
        else:
            # Fuori orario lavorativo nei giorni feriali
            consumo = base_load + np.random.normal(0.4, 0.15)
            
    return round(max(0.1, consumo), 2)  # Arrotonda ed evita valori negativi

df['consumo_kwh'] = df.apply(calcola_consumo, axis=1)

# 4. Funzione per generare la produzione solare (curva a campana)
def calcola_produzione_solare(row):
    ora = row['ora']
    
    # Il sole c'è solo tra le 7:00 e le 19:00
    if 7 <= ora <= 19:
        # Crea una curva a campana (seno) centrata alle ore 13:00
        x = (ora - 7) / 12 * np.pi
        produzione_ideale = potenza_fotovoltaico * np.sin(x)
        
        # Simula il meteo (50% soleggiato, 35% parzialmente nuvoloso, 15% molto nuvoloso)
        meteo = np.random.choice([1.0, 0.6, 0.15], p=[0.5, 0.35, 0.15])
        
        produzione = produzione_ideale * meteo + np.random.normal(0, 0.1)
        return round(max(0.0, produzione), 2)
    else:
        return 0.0

df['produzione_kwh'] = df.apply(calcola_produzione_solare, axis=1)

# 5. Calcolo dei flussi di energia (Logica Energetica)
# Autoconsumo: il minimo tra quanto produco e quanto consumo in quell'ora
df['autoconsumo_kwh'] = np.minimum(df['consumo_kwh'], df['produzione_kwh'])

# Immissione: la produzione solare che avanza e viene ceduta alla rete elettrica
df['immissione_rete_kwh'] = np.round(np.maximum(0.0, df['produzione_kwh'] - df['consumo_kwh']), 2)

# Prelievo: il consumo che non viene coperto dal solare e va acquistato dalla rete
df['prelievo_rete_kwh'] = np.round(np.maximum(0.0, df['consumo_kwh'] - df['produzione_kwh']), 2)

# Rimuoviamo le colonne temporanee di calcolo
df = df.drop(columns=['ora', 'giorno_settimana'])

# 6. Esportazione in CSV
df.to_csv('dati_consumi.csv', index=False)
print("File 'dati_consumi.csv' generato con successo! Contiene 744 righe (31 giorni x 24 ore).")