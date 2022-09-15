FROM ubuntu:18.10

COPY /app ./home/app
COPY ../dana ./home/dana

# Dana instalattion
ENV DANA_HOME=/home/dana/
ENV PATH "$PATH:${DANA_HOME}"
RUN echo "${PATH}" >> /etc/bash.bashrc
RUN chmod +x /home/dana/dana && chmod +x /home/dana/dnc
RUN chmod +x /home/app/distributor/run.sh

WORKDIR /home/app/distributor

CMD ["dana", "loop.o"]


