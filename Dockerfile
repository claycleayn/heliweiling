FROM gcc:latest
WORKDIR /usr/src/app
COPY random_sensor.c .
RUN gcc random_sensor.c -o /usr/local/bin/random_sensor
CMD ["/usr/local/bin/random_sensor"]