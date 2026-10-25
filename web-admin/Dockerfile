# ==============================================================================
# RoadSense Web Admin Portal - Production Multi-Stage Dockerfile
# ==============================================================================

# --- Stage 1: Build React/TypeScript App ---
FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies first for optimal Docker layer caching
COPY package*.json ./
RUN npm install

# Copy source files and build production bundle
COPY . .
RUN npm run build

# --- Stage 2: Lightweight Production Nginx Server ---
FROM nginx:alpine

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy built assets from builder stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration with SPA fallback and API proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose HTTP port
EXPOSE 80

# Run Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
