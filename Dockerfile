FROM node:18-alpine

RUN apk add --no-cache \
  chromium \
  nss \
  freetype \
  harfbuzz \
  ca-certificates \
  ttf-freefont \
  dbus \
  udev \
  libx11 \
  libxcomposite \
  libxdamage \
  libxtst \
  libnss \
  alsa-lib \
  at-spi2-core \
  mesa-dri-gallium \
  xvfb

# Set environment variables for Puppeteer
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser \
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_DISABLE_HEADLESS_WARNING=true

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
