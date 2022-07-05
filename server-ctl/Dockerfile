FROM python:3

WORKDIR /home/ubuntu/ServerCTL
COPY ../server-ctl .

RUN pip3 install kubernetes
RUN pip3 install pyyaml
RUN pip3 install flask
EXPOSE 5000

CMD ["sleep", "infinity"]
