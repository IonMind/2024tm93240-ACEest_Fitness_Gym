FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --create-home --uid 10001 appuser \
	&& chown appuser:appuser /app

COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser templates ./templates
COPY --chown=appuser:appuser tests ./tests

EXPOSE 5000

USER appuser

CMD ["python", "app.py"]