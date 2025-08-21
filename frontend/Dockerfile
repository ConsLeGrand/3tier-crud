FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY index.html app.js style.css /usr/share/nginx/html/
# config.js sera monté depuis un ConfigMap (modifiable sans rebuild)
EXPOSE 8080
