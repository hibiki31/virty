FROM ubuntu:20.04

# docker run -it ubuntu:20.04 bash
RUN apt-get update -y && apt-get install -y novnc websockify

EXPOSE 5999

CMD websockify --verbose --web /usr/share/novnc/ --token-plugin JSONTokenApi --token-source "http://localhost:8000/api/vms/vnc/%s" 5999