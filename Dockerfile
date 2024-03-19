FROM python:3.12.2

WORKDIR /app

RUN git clone https://github.com/danilnilne/speedtest-collector.git \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r speedtest-collector/requirements.txt

ENTRYPOINT ["python3", "speedtest-collector/start.py"]