# To build:
# export BROKER_USER=broker
# docker build -t deep_broker --build-arg BROKER_USER --rm=true .

FROM ubuntu:20.04
RUN apt-get update --fix-missing

ARG BROKER_USER=broker
ARG BROKER_HOME=/home/${BROKER_USER}
ARG MINICONDA_PATH=${BROKER_HOME}/miniconda
ARG MINICONDA_INSTALL_FILE=Miniconda3-py38_4.10.3-Linux-x86_64.sh
ARG UID_NUMBER=1006

RUN apt-get update --fix-missing && \
    DEBIAN_FRONTEND=noninteractive && \
    apt-get install -y --no-install-recommends tzdata && \
    apt-get install -y build-essential wget emacs git librdkafka-dev

# Add $BROKER_USER as user and create groups wheel and spt
RUN useradd -ms /bin/bash -u ${UID_NUMBER} $BROKER_USER && \
    addgroup wheel && \
    addgroup -gid 1003 scimma

# Add USER to wheel and to scimma
RUN usermod -aG wheel $BROKER_USER && \
    usermod -aG scimma $BROKER_USER

ENV MINICONDA_PATH ${MINICONDA_PATH}
USER ${BROKER_USER}
WORKDIR ${BROKER_HOME}

ENV USER $BROKER_USER
ENV HOME /home/$BROKER_USER
ENV SHELL /bin/bash

# Conda installation, using python38
RUN mkdir -p ${MINICONDA_PATH} \
    && cd ${MINICONDA_PATH} \
    && wget https://repo.anaconda.com/miniconda/${MINICONDA_INSTALL_FILE} \
    && chmod +x ${MINICONDA_INSTALL_FILE} \
    && ./${MINICONDA_INSTALL_FILE} -b -p ${MINICONDA_PATH} -u \
    && rm ${MINICONDA_INSTALL_FILE}

# Start the env and add channels and base dependencies
RUN . $MINICONDA_PATH/bin/activate && \
    conda update -n base -c defaults conda && \
    conda config --add channels conda-forge  && \
    conda install -y pip && \
    conda install -c conda-forge -y scipy=1.8.0 astropy healpy click

RUN . $MINICONDA_PATH/bin/activate && \
    pip install -U \
    mysql-connector-python-rf \
    ligo.skymap \
    keras-tcn==3.2.1 \
    hop-client \
    git+https://github.com/deepchatterjeeligo/astrorapid.git@ab8582e17015a55b9b3528a7dc320a3cfaf7d250


# Include Deep's scripts into the image
#RUN mkdir $HOME/broker_files
COPY broker_files broker_files

# Start with the right miniconda environment
RUN echo "export PYTHONPATH=${PYTHONPATH}:$HOME/broker_files" >> $HOME/.bashrc
RUN echo "export PATH=${PATH}:$HOME/broker_files" >> $HOME/.bashrc
RUN echo "source $MINICONDA_PATH/bin/activate" >> $HOME/.bashrc

# Use entrypoint script to start with conda and spt_cutter initialized
COPY --chown=${BROKER_USER}:${BROKER_USER} startup.sh .startup.sh
RUN chmod a+x .startup.sh
ENTRYPOINT ["bash",".startup.sh"]
