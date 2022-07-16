ARG WATCHDOG_VERSION=1.0.0
ARG OPENCV_VERSION=2.1.0

FROM edgerun/of-watchdog:$WATCHDOG_VERSION as watchdog
FROM edgerun/opencv:$OPENCV_VERSION

RUN apt update --allow-releaseinfo-change -y
COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

# Allows you to add additional packages via build-arg
ARG ADDITIONAL_PACKAGE

WORKDIR /home/app/

COPY index.py           .
COPY requirements.txt   .

RUN mkdir -p /home/app/python

ENV PATH=$PATH:/home/app/.local/bin:/home/app/python/bin/
ENV PYTHONPATH=$PYTHONPATH:/home/app/python

RUN pip3 install -r requirements.txt --extra-index-url=https://www.piwheels.org/simple --target=/home/app/python

RUN mkdir -p function
RUN touch ./function/__init__.py

WORKDIR /home/app/function/
COPY function/requirements.txt	.

RUN pip3 install -r requirements.txt --extra-index-url=https://www.piwheels.org/simple --target=/home/app/python
WORKDIR /home/app/


COPY function           function
RUN mkdir data
RUN chmod -R 777 /home/app/python


ENV fprocess="python3 index.py"
ENV cgi_headers="true"
ENV mode="http"
ENV upstream_url="http://127.0.0.1:5000"
EXPOSE 8080

HEALTHCHECK --interval=3s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]

