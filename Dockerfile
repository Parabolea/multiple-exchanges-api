FROM node:18-alpine

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
