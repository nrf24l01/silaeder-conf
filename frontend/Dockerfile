# Use the official lightweight NGINX image
FROM nginx:alpine

# Copy custom config and HTML file
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html

# Expose HTTP port
EXPOSE 80

# Default command
CMD ["nginx", "-g", "daemon off;"]
