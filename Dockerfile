FROM python:3.12-slim-bullseye

WORKDIR /myfitnessrank
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./MyFitnessRank.db .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
