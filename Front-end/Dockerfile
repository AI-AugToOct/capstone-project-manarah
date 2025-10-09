# syntax=docker/dockerfile:1.6
FROM node:18-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* yarn.lock* pnpm-lock.yaml* .npmrc* ./
RUN \
  if [ -f pnpm-lock.yaml ]; then corepack enable && corepack prepare pnpm@latest --activate && pnpm i --frozen-lockfile; \
  elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
  else npm ci; fi

FROM node:18-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN \
  if [ -f pnpm-lock.yaml ]; then corepack enable && pnpm build; \
  elif [ -f yarn.lock ]; then yarn build; \
  else npm run build; fi

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app ./
# Railway provides PORT; default for local is 4173
EXPOSE 4173
USER node
CMD sh -c "PORT=\${PORT:-4173}; \
  if [ -f pnpm-lock.yaml ]; then corepack enable && corepack prepare pnpm@latest --activate && pnpm dlx vite preview --host 0.0.0.0 --port \$PORT; \
  elif [ -f yarn.lock ]; then yarn dlx vite preview --host 0.0.0.0 --port \$PORT; \
  else npx vite preview --host 0.0.0.0 --port \$PORT; fi"
