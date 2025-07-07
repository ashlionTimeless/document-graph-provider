FROM python:3.10-slim

WORKDIR /app

RUN python -m pip install -U pip setuptools wheel spacy numpy flask langchain langdetect presidio_analyzer presidio_anonymizer
RUN python -m spacy download en
RUN python -m spacy download uk_core_news_sm
RUN python -m spacy download ru_core_news_sm

COPY . .

EXPOSE 4444

CMD ["python", "server.py"]
