FROM python:3.11.9-slim AS production
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip \
    && pip install --no-cache-dir --upgrade -r /app/requirements.txt \
    && apt -y update && apt -y install libopencv-dev
COPY ./src /app/src
CMD ["uvicorn", "src.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000", "--reload"]