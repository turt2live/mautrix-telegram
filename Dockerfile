FROM docker.io/alpine:3.7

ENV UID=1337 \
    GID=1337

COPY . /opt/mautrixtelegram
RUN apk add --no-cache \
      python3-dev \
      py3-virtualenv \
      py3-pillow \
      py3-aiohttp \
      py3-lxml \
      py3-magic \
      py3-numpy \
      py3-asn1crypto \
      py3-sqlalchemy \
      build-base \
      ffmpeg \
      bash \
      ca-certificates \
      su-exec \
      s6 \
      git \
      dos2unix \
 && cd /opt/mautrixtelegram \
 && cp -r docker/root/* / \
 && rm docker -rf \
 && pip3 install -r requirements.txt -r optional-requirements.txt \
 && dos2unix /etc/s6.d/.s6-svscan/finish \
 && dos2unix /etc/s6.d/mautrix-telegram/finish \
 && dos2unix /etc/s6.d/mautrix-telegram/run

VOLUME /data
EXPOSE 8080

CMD ["/bin/s6-svscan", "/etc/s6.d"]
