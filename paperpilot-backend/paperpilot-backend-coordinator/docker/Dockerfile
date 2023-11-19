FROM node:20-slim AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Change mirror
RUN rm -rf /etc/apt/sources.list.d/* \
    && touch /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian/ bookworm main contrib non-free non-free-firmware" | tee -a /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian/ bookworm-updates main contrib non-free non-free-firmware" | tee -a /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian/ bookworm-backports main contrib non-free non-free-firmware" | tee -a /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian-security bookworm-security main contrib non-free non-free-firmware" | tee -a /etc/apt/sources.list

COPY ./app.js /app/
COPY ./package.json /app/
COPY ./pnpm-lock.yaml /app/
WORKDIR /app

RUN pnpm install

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD [ "curl", "--include", "--no-buffer", "--header", "'Connection: close'", "--header", "'Upgrade: websocket'", "http://localhost:8000", "||", "exit", "1" ]

CMD [ "pnpm", "start" ]
