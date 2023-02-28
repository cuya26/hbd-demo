FROM node:16-alpine

USER root
WORKDIR /usr/src/app
RUN npm install -g @quasar/cli
ENTRYPOINT ["npm", "install", "&&", "quasar", "dev"]