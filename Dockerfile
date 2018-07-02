FROM cdrx/pyinstaller-linux:python3 AS build

RUN apt-get update
ENV APP_NAME='sam-cctv'

RUN mkdir /x_src
WORKDIR /x_src
ADD . /x_src
RUN pip3 install .
RUN pyinstaller --clean -y  --workpath /tmp  $APP_NAME.py -n $APP_NAME
RUN mkdir -p /x_src/dist/$APP_NAME/asynqp
RUN cp /usr/local/lib/*/*/asynqp/amqp*.xml /x_src/dist/$APP_NAME/asynqp/


# This results in a sing layer image
# FROM  ubuntu:16.04
# RUN apt-get update

FROM debian:9-slim

ENV APP_NAME='sam-cctv'

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV TZ=Asia/Shanghai
RUN echo $TZ > /etc/timezone && \
    apt-get install -y tzdata && \
    rm /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean

# clean
RUN apt-get autoremove \
    && rm -rf /var/cache/apt/* \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=build /x_src/dist/sam-cctv /app

EXPOSE 80 15570
ENV NAME cctv

# need to set env for app
ENV CCTV_TYPE km
ENV CCTV_SVR http://cctv-server:7080
ENV SVC_AMQP amqp://guest:guest@rabbit:5672//
ENV SVC_PORT 80
ENV SVC_QID 0

# run the application
COPY ./entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["sam-cctv"]
