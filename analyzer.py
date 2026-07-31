import pandas as pd

def analizza_dati_energia(file_path: str):
    # Load the CSV file
    df = pd.read_csv(file_path)
    
    # Ensure the timestamp is in datetime format
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    
    # 1. Overall Calculations
    total_consumption = round(df['consumo_kwh'].sum(), 2)
    total_production = round(df['produzione_kwh'].sum(), 2)
    total_self_consumption = round(df['autoconsumo_kwh'].sum(), 2)
    
    # 2. Solar Self-Consumption Rate
    self_consumption_rate = 0
    if total_production > 0:
        self_consumption_rate = round((total_self_consumption / total_production) * 100, 2)
        
    # 3. Night Consumption Analysis (22:00 - 06:00)
    night_consumption = df[(df['hour'] >= 22) | (df['hour'] <= 6)]['consumo_kwh'].sum()
    day_consumption = df[(df['hour'] > 6) & (df['hour'] < 22)]['consumo_kwh'].sum()
    night_pct = round((night_consumption / (night_consumption + day_consumption)) * 100, 2)
    
    # 4. Find the Peak Consumption Hour
    peak_row = df.loc[df['consumo_kwh'].idxmax()]
    peak_val = peak_row['consumo_kwh']
    peak_time = peak_row['timestamp'].strftime('%Y-%m-%d %H:%M')
    
    # Dictionary with the resulting stats matching main.py
    statistiche = {
        "consumo_totale_kwh": total_consumption,
        "produzione_totale_kwh": total_production,
        "autoconsumo_totale_kwh": total_self_consumption,
        "tasso_autoconsumo_percento": self_consumption_rate,
        "percentuale_consumo_notturno": night_pct,
        "picco_massimo_kwh": peak_val,
        "data_ora_picco": peak_time
    }
    
    return statistiche