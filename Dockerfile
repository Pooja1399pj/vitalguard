FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN ls -la /app/data/*.csv || echo "CSV FILES MISSING IN IMAGE"

EXPOSE 8080

CMD ["python", "-m", "streamlit", "run", "dashboard.py", \
     "--server.port=8080", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false"]