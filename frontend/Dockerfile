FROM node:22-slim

WORKDIR /app
COPY package.json tsconfig.json index.html ./
COPY src ./src
COPY public ./public
RUN npm install
CMD ["npm", "run", "dev"]
