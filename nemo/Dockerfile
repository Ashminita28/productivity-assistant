FROM python:3.10-slim
WORKDIR /app
RUN pip install nemoguardrails==0.9.1
COPY ./config /config
EXPOSE 8001
CMD ["nemoguardrails", "server", "--port", "8001", "--config", "/config"]
