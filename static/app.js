let myChart = null;

// Gestione dell'avvio dell'applicazione
window.addEventListener('load', () => {
    // 1. Inizializzazione del Grafico
    const ctx = document.getElementById('energyChart').getContext('2d');
    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
            datasets: [
                { label: 'Consumption (kWh)', data: [1.2, 1.1, 4.5, 9.2, 7.8, 2.1], borderColor: '#06b6d4', tension: 0.4 },
                { label: 'Solar Production (kWh)', data: [0, 0, 1.2, 5.8, 3.1, 0], borderColor: '#10b981', tension: 0.4 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { grid: { color: 'rgba(255,255,255,0.05)' } }
            }
        }
    });

    // 2. Caricamento dati iniziali dal server
    caricaDatiIniziali();

    // 3. Collegamento dei bottoni agli eventi (Event Listeners)
    document.getElementById('btn-send').addEventListener('click', inviaMessaggio);
    document.getElementById('btn-export').addEventListener('click', exportToPDF);
    
    // Invio messaggio premendo il tasto "Invio"
    document.getElementById('user-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') inviaMessaggio();
    });
});

async function caricaDatiIniziali() {
    try {
        const response = await fetch('/api/analizza-e-chiedi', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ domanda: "Give me a summary of my energy usage." })
        });
        const data = await response.json();
        aggiornaDashboard(data.statistiche);
    } catch (error) {
        console.error("Unable to load initial data:", error);
    }
}

function aggiornaDashboard(stats) {
    document.getElementById('stat-consumo').innerText = stats.consumo_totale_kwh + " kWh";
    document.getElementById('stat-produzione').innerText = stats.produzione_totale_kwh + " kWh";
    document.getElementById('stat-autoconsumo').innerText = stats.tasso_autoconsumo_percento + " %";
    document.getElementById('stat-notturno').innerText = stats.percentuale_consumo_notturno + " %";
}

async function inviaMessaggio() {
    const input = document.getElementById('user-input');
    const query = input.value.trim();
    if (!query) return;

    aggiungiMessaggio(query, 'user');
    input.value = '';

    const loadingId = aggiungiMessaggio('Analyzing data...', 'ai');

    try {
        const response = await fetch('/api/analizza-e-chiedi', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ domanda: query })
        });
        
        const data = await response.json();
        rimuoviMessaggio(loadingId);
        aggiungiMessaggio(data.risposta_ai, 'ai');
        aggiornaDashboard(data.statistiche);
        
    } catch (error) {
        rimuoviMessaggio(loadingId);
        aggiungiMessaggio("Error: unable to connect to the server.", 'ai');
    }
}

function aggiungiMessaggio(testo, mittente) {
    const chat = document.getElementById('chat-messages');
    const div = document.createElement('div');
    const id = 'msg-' + Date.now();
    div.id = id;
    div.className = `message ${mittente}`;
    div.textContent = testo;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
    return id;
}

function rimuoviMessaggio(id) {
    const msg = document.getElementById(id);
    if (msg) msg.remove();
}

async function exportToPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
    });

    // Intestazione Report
    doc.setFillColor(11, 15, 25);
    doc.rect(0, 0, 210, 40, 'F');
    
    doc.setTextColor(255, 255, 255);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(22);
    doc.text("AMPERE TRANSITION", 20, 20);
    
    doc.setFont("helvetica", "normal");
    doc.setFontSize(11);
    doc.text("Digital Solutions - Smart Meter Energy Report", 20, 28);
    
    const dataCorrente = new Date().toLocaleString('en-US', { timeZone: 'UTC' });
    doc.setFontSize(9);
    doc.setTextColor(156, 163, 175);
    doc.text(`Generated (UTC): ${dataCorrente}`, 130, 28);

    // Sezione Metriche
    doc.setTextColor(11, 15, 25);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(14);
    doc.text("Energy Summary Metrics", 20, 55);
    doc.setDrawColor(229, 231, 235);
    doc.line(20, 58, 190, 58);

    const consumo = document.getElementById('stat-consumo').innerText;
    const produzione = document.getElementById('stat-produzione').innerText;
    const autoconsumo = document.getElementById('stat-autoconsumo').innerText;
    const notturno = document.getElementById('stat-notturno').innerText;

    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.setTextColor(55, 65, 81);
    
    doc.setFont("helvetica", "bold"); doc.text("Total Consumption:", 20, 70);
    doc.setFont("helvetica", "normal"); doc.text(consumo, 60, 70);
    
    doc.setFont("helvetica", "bold"); doc.text("Solar Production:", 20, 80);
    doc.setFont("helvetica", "normal"); doc.text(produzione, 60, 80);
    
    doc.setFont("helvetica", "bold"); doc.text("Self-Consumption:", 110, 70);
    doc.setFont("helvetica", "normal"); doc.text(autoconsumo, 155, 70);
    
    doc.setFont("helvetica", "bold"); doc.text("Night Consumption:", 110, 80);
    doc.setFont("helvetica", "normal"); doc.text(notturno, 155, 80);

    // Sezione Grafico
    doc.setFont("helvetica", "bold");
    doc.setFontSize(14);
    doc.setTextColor(11, 15, 25);
    doc.text("Energy Load Profile", 20, 105);
    doc.line(20, 108, 190, 108);

    const chartCanvas = document.getElementById('energyChart');
    const chartImage = chartCanvas.toDataURL('image/png', 1.0);
    doc.addImage(chartImage, 'PNG', 20, 115, 170, 85);

    // Footer
    doc.setFontSize(9);
    doc.setTextColor(156, 163, 175);
    doc.text("Confidential Report - Generated by Ampere Smart Meter Analyst Engine", 20, 275);
    doc.text("Page 1 of 1", 175, 275);

    doc.save("Ampere_Energy_Report.pdf");
}