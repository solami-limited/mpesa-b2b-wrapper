FROM nginx:alpine3.17-slim
LABEL authors="clov"

RUN rm /etc/nginx/conf.d/default.conf
COPY ../.devops/nginx/nginx.conf /etc/nginx/conf.d/default.conf
