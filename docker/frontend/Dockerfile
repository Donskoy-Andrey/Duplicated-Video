FROM node:20.10.0

WORKDIR /app

COPY ./duplicates/frontend/package*.json ./

#COPY ./semantic/frontend/.env.local /app/.env.local

RUN npm ci
