from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import requests
import os
import traceback  # <--- Importante per stampare gli errori completi
from analyzer import analizza_dati_energia

app = FastAPI(title="Smart Meter Analyst API")

# --- SECURITY MIDDLEWARE ---
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    # Abbiamo aggiunto 'data:' e 'https://fonts.gstatic.com' per permettere il caricamento corretto dei font
    response.headers["Content-Security-Policy"] = "default-src 'self' data: https://fonts.googleapis.com https://fonts.gstatic.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com;"
    return response

app.mount("/static", StaticFiles(directory="static"), name="static")

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2"
SECURE_CSV_PATH = "dati_consumi.csv"

class ChatRequest(BaseModel):
    domanda: str = Field(..., min_length=1, max_length=1000)

@app.get("/")
async def get_index():
    return FileResponse("static/index.html")

@app.post("/api/analizza-e-chiedi")
async def analizza_e_chiedi(request: ChatRequest):
    query_clean = request.domanda.strip()
    if not query_clean:
        raise HTTPException(status_code=400, detail="The question cannot be empty.")

    if not os.path.exists(SECURE_CSV_PATH):
        raise HTTPException(status_code=404, detail="Energy database not available.")
    
    # 1. Prova l'analisi Pandas e se fallisce stampa l'errore esatto
    try:
        statistiche = analizza_dati_energia(SECURE_CSV_PATH)
    except Exception as e:
        print("\n=== ERRORE NEL MODULO ANALYZER ===")
        traceback.print_exc()  # <--- Stampa l'errore completo con la riga che fallisce nel terminale
        print("==================================\n")
        raise HTTPException(status_code=500, detail=f"Analyzer Error: {str(e)}")
    
    prompt_sistema = f"""
    You are an expert Energy Consultant from Ampere Transition.
    Analyze the real smart meter data provided below and answer the user's question.
    If the question is not related to energy consumption or sustainability, politely reply that you can only address energy and sustainability topics.

    REAL CUSTOMER DATA:
    - Total Consumption: {statistiche['consumo_totale_kwh']} kWh
    - Total Solar Production: {statistiche['produzione_totale_kwh']} kWh
    - Self-Consumed Energy: {statistiche['autoconsumo_totale_kwh']} kWh
    - Solar Self-Consumption Rate: {statistiche['tasso_autoconsumo_percento']}%
    - Night Consumption Rate (22:00 - 06:00): {statistiche['percentuale_consumo_notturno']}%
    - Peak Demand: {statistiche['picco_massimo_kwh']} kW recorded on {statistiche['data_ora_picco']}
    """

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": query_clean}
        ],
        "stream": False
    }

    # 2. Prova a chiamare Ollama e se fallisce stampa l'errore esatto
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        risultato_ai = response.json()
        risposta_testo = risultato_ai["message"]["content"]
    except Exception as e:
        print("\n=== ERRORE COMUNICAZIONE OLLAMA ===")
        traceback.print_exc()  # <--- Stampa l'errore completo nel terminale
        print("====================================\n")
        raise HTTPException(status_code=500, detail=f"Ollama Error: {str(e)}")

    return {
        "risposta_ai": risposta_testo,
        "statistiche": statistiche
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)