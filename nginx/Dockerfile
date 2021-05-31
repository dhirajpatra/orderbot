FROM nginx:1.19.0-alpine

RUN rm -rf /etc/nginx/conf.d/default.conf
COPY ./conf.d/local.conf /etc/nginx/conf.d/default.conf
COPY ./conf.d/nginx.htpasswd /etc/nginx/conf.d/nginx.htpasswd

RUN chmod -R 777 /var/log/

CMD ["nginx", "-g", "daemon off;"]