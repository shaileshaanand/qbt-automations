FROM python:3.13-alpine AS build

# install uv
RUN pip install --no-cache-dir uv

# install patchelf
RUN apk add --no-cache gcc musl-dev python3-dev patchelf

WORKDIR /app
COPY pyproject.toml .
COPY uv.lock .
RUN uv sync

COPY . .

RUN uv run python -m nuitka \
    --onefile main.py \
    --output-dir=build \
    --output-filename=qb-automations

FROM alpine:latest

WORKDIR /app

COPY --from=build /app/build/qb-automations .

ENTRYPOINT ["/app/qb-automations"]