FROM node:20-slim AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable
COPY ./app.js /app/
COPY ./package.json /app/
COPY ./pnpm-lock.yaml /app/
WORKDIR /app

RUN pnpm install

EXPOSE 8000
CMD [ "pnpm", "start" ]