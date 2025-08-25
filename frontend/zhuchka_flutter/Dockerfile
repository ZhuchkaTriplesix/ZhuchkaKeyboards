# Multi-stage Dockerfile for Flutter Web build served by Nginx

# 1) Build stage: use Flutter SDK image
FROM ghcr.io/cirruslabs/flutter:stable AS build
WORKDIR /app

# Show Flutter version for debugging/caching
RUN flutter --version

# Cache pub dependencies
COPY pubspec.yaml ./
COPY analysis_options.yaml ./
RUN flutter pub get

# Copy the rest of the project
COPY . .

# Ensure platforms exist (web, android, ios, etc.)
RUN flutter create .

# Fetch packages (again in case new files affect deps) and build web release
RUN flutter pub get && \
    flutter build web --release --no-tree-shake-icons


# 2) Runtime stage: serve with Nginx
FROM nginx:alpine

# Copy nginx config and web build
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/build/web /usr/share/nginx/html

# Entrypoint to inject runtime API_BASE_URL into Flutter asset (assets/env)
COPY docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV API_BASE_URL=http://localhost:8001
EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]


