FROM python:3.9-slim
WORKDIR /bot
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY main.py migrations.py parsers.py validators.py db.py ./
CMD ["python3", "main.py"]