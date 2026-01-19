FROM python:3.9-slim

# Imposta la cartella di lavoro nel contenitore
WORKDIR /app

# 1. Copia il file requirements dalla cartella src (visto che lì si trova)
COPY src/requirements.txt .

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copia lo scraper dalla cartella principale (visto che lì si trova)
# Nota: NON scriviamo src/scraper.py perché nel tuo screen è fuori!
COPY scraper.py .

# Comando per avviare lo script
CMD ["python", "scraper.py"]