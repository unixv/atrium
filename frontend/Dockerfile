FROM node:22-slim

WORKDIR /app
COPY package.json package-lock.json tsconfig.json index.html vite.config.ts ./
COPY src ./src
COPY public ./public
RUN npm ci --registry=https://registry.npmjs.org
CMD ["npm", "run", "dev"]
