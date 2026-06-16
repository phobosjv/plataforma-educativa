# --- Etapa 1: build estático de la SPA ---
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build          # genera /app/dist (tsc -b && vite build)

# --- Etapa 2: servir con nginx (sin servidor de desarrollo) ---
# La config (nginx/frontend.conf) se monta como volumen desde docker-compose,
# igual que el sandbox. Sirve la SPA y proxya /api y /media al servicio api.
FROM nginx:alpine
# Parches de seguridad del SO (Alpine) posteriores a la imagen base.
RUN apk upgrade --no-cache
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
