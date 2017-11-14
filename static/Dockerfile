FROM node:8.8 as builder
COPY ./app/ /root/app/
WORKDIR /root/app/
RUN ./build.sh

FROM nginx:mainline
COPY server.conf /etc/nginx/nginx.conf
COPY --from=builder /root/app/build/ /usr/share/nginx/html/
