FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV PORT=7860

# Expose the port Hugging Face uses
EXPOSE 7860

CMD ["python", "app.py"]
