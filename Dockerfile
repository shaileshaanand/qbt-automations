FROM python:3.13-slim AS build

# install uv
RUN pip install --no-cache-dir uv

# install patchelf
RUN apt-get update && \
    apt-get install -y patchelf gcc && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean && \
    apt-get autoremove -y

WORKDIR /app
COPY pyproject.toml .
COPY uv.lock .
RUN uv sync

COPY . .

RUN uv run python -m nuitka \
    --onefile main.py \
    --output-dir=build \
    --output-filename=qb-automations

FROM gcr.io/distroless/base

WORKDIR /app

COPY --from=build /app/build/qb-automations .

ENTRYPOINT ["/app/qb-automations"]