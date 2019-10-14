FROM centos:8

# ENV http_proxy "http://IP:PORT/"
# ENV https_proxy "http://IP:PORT/"

COPY ./conf/nginx.repo /etc/yum.repos.d/nginx.repo
RUN dnf install -y nginx

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]