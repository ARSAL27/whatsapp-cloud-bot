FROM node:20-slim

# Install Chromium and dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf libxss1 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Puppeteer
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

WORKDIR /app

# Grant permissions for LocalAuth storage
RUN mkdir -p /app/.wwebjs_auth && chmod -R 777 /app/.wwebjs_auth

COPY package*.json ./
RUN npm install

COPY . .

# Hugging Face Spaces use port 7860 by default
EXPOSE 7860
ENV PORT=7860

CMD ["node", "index.js"]
