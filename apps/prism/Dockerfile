# Owner Portal - production build

FROM node:20-alpine AS build
WORKDIR /app

# Install deps first (leverage layer caching)
COPY apps/portal/package.json apps/portal/package-lock.json ./
RUN npm ci

COPY apps/portal .

# Allow overriding API base at build-time (default: https://api.localhost)
ARG VITE_OWNER_API_BASE_URL=https://api.localhost
ENV VITE_OWNER_API_BASE_URL=$VITE_OWNER_API_BASE_URL

RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
# Simple gzip/static config (nginx default is fine for now)
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
