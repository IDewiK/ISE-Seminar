FROM python:2
COPY ./install.sh /src/install.sh

RUN /src/install.sh

CMD ["/bin/bash"]