FROM ubuntu:18.10

COPY ../app .
COPY ../dana .
COPY ../naive.yaml .

# Dana instalattion
RUN chmod 755 ~/dana
ENV DANA_HOME=~/dana/
ENV PATH="${PATH}:${DANA_HOME}"

# Cluster configuration
CMD ["kubectl", "apply", "-f", "./naive.yaml"]

WORKDIR ~/app/distributor

#CMD ["dana", "-sp","../readn","RemoteDist.o","5000","5001"]
#ENTRYPOINT ["/bin/bash", "./../scripts/bash/remotedist.sh"]
CMD ["dana", "loop.o"]
