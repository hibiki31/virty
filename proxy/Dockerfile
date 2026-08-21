FROM ubuntu:24.04@sha256:33ceb71981b602c1a7443a53469e4dba065f7503eab3078a2d7a57a2ab987517

# docker run -it ubuntu:24.04 bash
RUN apt-get update -y && apt-get install -y novnc websockify

EXPOSE 5999

CMD websockify --web /usr/share/novnc/ --token-plugin JSONTokenApi --token-source "http://localhost:8000/api/vms/vnc/%s" 5999
