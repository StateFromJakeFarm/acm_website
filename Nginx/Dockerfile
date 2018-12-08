FROM nginx:latest
RUN rm /etc/nginx/conf.d/default.conf /etc/nginx/nginx.conf
COPY ./sites-enabled /etc/nginx/conf.d
COPY ./nginx.conf /etc/nginx/nginx.conf
