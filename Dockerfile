FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

COPY requirements.txt .

# Install build-essential, cmake, Boost libraries, and other dependencies
RUN apt-get update && \
  apt-get install -y wget build-essential cmake libboost-all-dev git unzip && \
  apt-get install -y zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev liblzma-dev && \
  rm -rf /var/lib/apt/lists/*

# Download and install Python 3.10 from source with -fPIC
RUN wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz && \
  tar -xvf Python-3.10.0.tgz && \
  cd Python-3.10.0 && \
  CFLAGS="-fPIC" ./configure --enable-optimizations && \
  make -j $(nproc) && \
  make altinstall && \
  cd .. && \
  rm -rf Python-3.10.0 Python-3.10.0.tgz

# Create symbolic links for python3 and pip3 to point to python3.10 and pip3.10
RUN ln -sf /usr/local/bin/python3.10 /usr/bin/python3 && \
  ln -sf /usr/local/bin/pip3.10 /usr/bin/pip3

# Install Python dependencies including pybind11
RUN pip3 install --no-cache-dir -r requirements.txt && \
  pip3 install pybind11

# Set pybind11_DIR environment variable
ENV pybind11_DIR="/usr/local/lib/python3.10/site-packages/pybind11/share/cmake/pybind11"

# Download and install OGDF with -fPIC
RUN wget https://ogdf.uos.de/wp-content/uploads/2020/02/ogdf.v2020.02.zip && \
  unzip ogdf.v2020.02.zip && \
  rm ogdf.v2020.02.zip && \
  cd OGDF && \
  mkdir build && cd build && \
  cmake -DCMAKE_POSITION_INDEPENDENT_CODE=ON .. && \
  make -j4 && \
  make install

# Install Rapidjson
RUN wget https://github.com/Tencent/rapidjson/archive/v1.1.0.tar.gz -O rapidjson.tar.gz && \
  tar -xzf rapidjson.tar.gz && \
  rm rapidjson.tar.gz && \
  cp -r rapidjson-1.1.0/include/rapidjson /usr/local/include && \
  rm -rf rapidjson-1.1.0

# Copy the source files
COPY . .

# Build the Annotation Graph
RUN mkdir -p /app/annotation-graph/build && \
  cd /app/annotation-graph/build && \
  cmake -DCMAKE_POSITION_INDEPENDENT_CODE=ON .. && \
  make && \
  make install

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]

