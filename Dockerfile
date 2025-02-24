FROM node:18-alpine

# Set environment variables for Puppeteer
ENV CHROME_BIN="/usr/bin/chromium-browser" \
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD="true"

RUN set -x \
    && apk update \
    && apk upgrade \
    && apk add --no-cache \
    udev \
    ttf-freefont \
    chromium \
    && npm install puppeteer@1.10.0

WORKDIR /app

RUN apk add --no-cache python3 py3-pip

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages

#RUN python -m venv my-venv
#
#RUN my-venv/bin/pip install websockets asyncio nest_asyncio

COPY package.json yarn.lock ./

RUN yarn install

COPY . .

CMD ["yarn", "start"]
