FROM node:16-buster
WORKDIR /app

COPY . .

RUN yarn install
RUN yarn build

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["yarn", "start"]