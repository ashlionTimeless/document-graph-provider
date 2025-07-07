FROM python:3.10-slim

WORKDIR /app

RUN python -m pip install -U pip setuptools numpy
RUN python -m pip install graphrag
RUN python -m pip install dotenv flask neo4j llama_index neo4j-driver pandas

COPY . .

EXPOSE 6000

CMD ["python", "src/index.py"]
