FROM node:18-alpine

# Install dependencies required for Puppeteer
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    font-noto \
    font-noto-cjk \
    font-noto-emoji \
    libstdc++ \
    chromium-chromedriver \
    bash \
    libx11 \
    libxcomposite \
    libxrandr \
    libxfixes \
    libxi \
    libxcursor \
    libxdamage \
    pango \
    glib \
    alsa-lib \
    dbus dbus-x11 \
    wget \
    # Additional dependencies for Puppeteer
    gconf \
    alsa-lib \
    atk \
    cairo \
    cups \
    dbus \
    expat \
    fontconfig \
    gdk-pixbuf \
    glib \
    gtk+3.0 \
    nspr \
    pango \
    xcb-util \
    libx11 \
    libx11-xcb \
    libxcb \
    libxcomposite \
    libxcursor \
    libxdamage \
    libxext \
    libxfixes \
    libxi \
    libxrandr \
    libxrender \
    libxss \
    libxtst \
    libnss \
    lsb-release \
    xdg-utils \
    fonts-liberation

# Set environment variables for Puppeteer
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true

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
