FROM python:3.12-slim
WORKDIR /src
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 libxcb1 \
    && rm -rf /var/lib/apt/lists/*
COPY ./requirements.txt /src/requirements.txt
RUN pip install --no-cache-dir -r /src/requirements.txt
COPY ./src /src/src
COPY ./onnx_output /src/onnx_output
ENV ONNX_MODEL_PATH=/src/onnx_output
CMD sh -c "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-80}"