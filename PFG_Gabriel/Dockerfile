FROM ubuntu:18.10

COPY ./dana ./home/renato/dana
RUN chmod 755 ./home/renato/dana
COPY . ./home/renato/dist
ENV DANA_HOME=/home/renato/dana/
ENV PATH="${PATH}:/home/renato/dana/"
WORKDIR /home/renato/dist/distributor

#CMD ["dana", "-sp","../readn","RemoteDist.o","5000","5001"]
#ENTRYPOINT ["/bin/bash", "./../scripts/bash/remotedist.sh"]
CMD ["dana", "loop.o"]
