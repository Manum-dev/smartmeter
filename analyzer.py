import pandas as pd

def analizza_dati_energia(file_path: str):
    # Carica il file CSV
    df = pd.read_csv(file_path)
    
    # Assicurati che il timestamp sia in formato datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['ora'] = df['timestamp'].dt.hour
    
    # 1. Calcoli generali
    consumo_totale = round(df['consumo_kwh'].sum(), 2)
    produzione_totale = round(df['produzione_kwh'].sum(), 2)
    autoconsumo_totale = round(df['autoconsumo_kwh'].sum(), 2)
    
    # 2. Percentuale di autoconsumo (quanta energia prodotta è stata usata)
    tasso_autoconsumo = 0
    if produzione_totale > 0:
        tasso_autoconsumo = round((autoconsumo_totale / produzione_totale) * 100, 2)
        
    # 3. Analisi consumi notturni (dalle 22:00 alle 06:00)
    consumo_notturno = df[(df['ora'] >= 22) | (df['ora'] <= 6)]['consumo_kwh'].sum()
    consumo_diurno = df[(df['ora'] > 6) & (df['ora'] < 22)]['consumo_kwh'].sum()
    percentuale_notturno = round((consumo_notturno / (consumo_notturno + consumo_diurno)) * 100, 2)
    
    # 4. Trova il picco massimo di consumo
    riga_picco = df.loc[df['consumo_kwh'].idxmax()]
    picco_valore = riga_picco['consumo_kwh']
    picco_data = riga_picco['timestamp'].strftime('%Y-%m-%d %H:%M')
    
    # Prepariamo un dizionario con i risultati da passare all'API e all'LLM
    statistiche = {
        "consumo_totale_kwh": consumo_totale,
        "produzione_totale_kwh": produzione_totale,
        "autoconsumo_totale_kwh": autoconsumo_totale,
        "tasso_autoconsumo_percento": tasso_autoconsumo,
        "percentuale_consumo_notturno": percentuale_notturno,
        "picco_massimo_kwh": picco_valore,
        "data_ora_picco": picco_data
    }
    
    return statistiche