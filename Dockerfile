FROM alpine:latest

WORKDIR /home
RUN apk update && apk add python3 git
RUN pip3 install bottle redis
RUN git clone https://github.com/atmarkatmark/teams-redirector-server.git

WORKDIR /home/teams-redirector-server
RUN sed -i -e "s/run(host='localhost'/run(host='0.0.0.0'/g" teams-redirector.py
RUN sed -i -e "s/Redis(host='localhost'/Redis(host='redirector-redis'/g" teams-redirector.py
CMD python3 teams-redirector.py
EXPOSE 8080

