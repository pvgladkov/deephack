FROM centos:7.2.1511
MAINTAINER artyom.korkhov@gmail.com

RUN yum -y install epel-release

RUN yum -y update && \
    yum install -y libjpeg-turbo-devel zlib-devel saslwrapper-devel cyrus-sasl-devel \
    libxml2-devel libxslt-devel lapack-devel liblas-devel libffi-devel postgresql-devel \
    rsync grep screen tzdata redhat-lsb-core wget python-pip python-devel
RUN yum groupinstall -y "Development tools" && yum clean all

RUN groupadd -r deephack && useradd -r -m -g deephack deephack
RUN mkdir -p /home/deephack/turing /var/log/deephack && \
    chown deephack:deephack /home/deephack/turing /var/log/deephack

RUN pip install --upgrade pip

COPY requirements.txt /home/deephack/
RUN pip install -r /home/deephack/requirements.txt


COPY ./ /home/deephack/turing/

WORKDIR /home/deephack/turing

