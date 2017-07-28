FROM ubuntu

RUN apt-get update && apt-get install -y \
		bc \
		build-essential \
		cmake \
		curl \
		g++ \
		gfortran \
		git \
		libffi-dev \
		libfreetype6-dev \
		libhdf5-dev \
		libjpeg-dev \
		liblcms2-dev \
		libopenblas-dev \
		liblapack-dev \
		libssl-dev \
		libtiff5-dev \
		libwebp-dev \
		libzmq3-dev \
		nano \
		pkg-config \
		python-dev \
		software-properties-common \
		unzip \
		vim \
		wget \
		zlib1g-dev \
		&& \
	apt-get clean && \
	apt-get autoremove && \
	rm -rf /var/lib/apt/lists/* && \
# Link BLAS library to use OpenBLAS using the alternatives mechanism (https://www.scipy.org/scipylib/building/linux.html#debian-ubuntu)
	update-alternatives --set libblas.so.3 /usr/lib/openblas-base/libblas.so.3

# Install pip
RUN curl -O https://bootstrap.pypa.io/get-pip.py && \
	python get-pip.py && \
	rm get-pip.py

# Add SNI support to Python
RUN pip --no-cache-dir install \
		pyopenssl \
		ndg-httpsclient \
		pyasn1


# Install other useful Python packages using pip
RUN pip --no-cache-dir install --upgrade ipython && \
	pip --no-cache-dir install \
		Cython \
		ipykernel \
		jupyter \
		path.py \
		Pillow \
		pygments \
		six \
		sphinx \
		wheel \
		zmq \
		&& \
	python -m ipykernel.kernelspec

RUN groupadd -r deephack && useradd -r -m -g deephack deephack
RUN mkdir -p /home/deephack/turing /var/log/deephack && \
    chown deephack:deephack /home/deephack/turing /var/log/deephack

RUN pip install --upgrade pip

COPY requirements.txt /home/deephack/
RUN pip install -r /home/deephack/requirements.txt

WORKDIR /home/deephack/turing

RUN git clone --recursive https://github.com/dmlc/xgboost xgboost
RUN cd xgboost; make -j4

RUN cd xgboost/python-package && python setup.py install

COPY ./ /home/deephack/turing/

RUN export PYTHONPATH=$PYTHONPATH:/home/deephack/turing/xgboost/python-package:/home/deephack/turing/src/

RUN mkdir /home/deephack/turing/srilm-1.7.2 && \
	tar -xvf srilm-1.7.2.tar.gz --directory /home/deephack/turing/srilm-1.7.2
RUN cd /home/deephack/turing/srilm-1.7.2 && \
 	sed -i -- 's/# SRILM = \/home\/speech\/stolcke\/project\/srilm\/devel/SRILM = \/home\/deephack\/turing\/srilm-1.7.2/g' Makefile && \
 	make World

ENV SRILM=/home/deephack/turing/srilm-1.7.2/bin/i686-m64/ngram
ENV NGRAM_MODEL=/home/deephack/turing/europarl.en.srilm
ENV HOME_DIR=/home/deephack/turing/
ENV SRC_DIR=/home/deephack/turing/src/
ENV MODEL_PATH=/home/deephack/turing/2.model



RUN python -c "import nltk; nltk.download('brown')"
RUN python -m spacy download en

RUN pip install simplejson
