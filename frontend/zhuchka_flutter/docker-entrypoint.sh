#!/bin/sh
set -e

# Inject API_BASE_URL into Flutter env asset at runtime if present
if [ -n "$API_BASE_URL" ]; then
  if [ -f /usr/share/nginx/html/assets/env ]; then
    echo "API_BASE_URL=$API_BASE_URL" > /usr/share/nginx/html/assets/env
  fi
fi

# Start nginx
exec nginx -g 'daemon off;'
