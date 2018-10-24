FROM ubuntu:bionic
MAINTAINER Balance

RUN apt-get update && \
    apt-get -y dist-upgrade && \
    apt-get -y install python3 build-essential ssh \
               ruby ruby-dev rubygems \
               python3-simplejson python3-setuptools

RUN gem install --no-ri --no-rdoc fpm

ADD . /root/indexer

WORKDIR /root/indexer

RUN python3 -m compileall balance_indexer

ARG VERSION
RUN fpm -n balance-indexer -v ${VERSION} \
    --python-package-name-prefix=python3 \
    --python-bin=/usr/bin/python3 \
    --python-install-bin=/usr/bin \
    --python-install-lib=/usr/lib/python3/dist-packages \
    --deb-systemd=systemd/balance-indexer.service \
    --after-install=debian/postinst \
    -s python -t deb .

ADD private-deb-repo-key .
RUN tar -c *.deb | ssh -oStrictHostKeyChecking=no -i /root/indexer/private-deb-repo-key apt@apt.balance.io
