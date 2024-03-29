FROM python:3.12-slim-bookworm AS build

RUN apt update && apt upgrade -y && apt install -y --no-install-recommends patch gcc g++

WORKDIR /app
ADD requirements.txt /app
RUN pip install -r requirements.txt --no-cache-dir
ADD patches /app/patches
RUN patch -p1 /usr/local/lib/python3.12/site-packages/paddleocr/paddleocr.py patches/paddleocr-import.patch

FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt update && apt install -y --no-install-recommends libgomp1 libgl1 libglib2.0-0

COPY --from=build /usr/local/bin /usr/local/bin
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

ADD model/ /app/model
ADD api.py /app

CMD ["uvicorn", "api:app", "--host", "0.0.0.0"]