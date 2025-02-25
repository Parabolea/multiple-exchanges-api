FROM node:18-alpine

WORKDIR /usr/app

ENV CHROME_BIN="/usr/bin/chromium-browser" \
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD="true"
RUN set -x \
    && apk update \
    && apk upgrade \
    && apk add --no-cache \
    udev \
    chromium \
    nss \
    freetype \
    freetype-dev \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    dbus \
    && npm cache clean --force


# Install Python & dependencies
RUN apk add --no-cache python3 py3-pip dbus

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages

COPY package.json yarn.lock ./

RUN yarn install --frozen-lockfile

COPY . .

# Start the dbus service before running the application
CMD ["yarn", "start"]

EXPOSE 8080
