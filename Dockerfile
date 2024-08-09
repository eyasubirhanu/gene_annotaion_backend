FROM python:3.10

WORKDIR /app

COPY requirements.txt .

# Install build-essential, cmake, Boost libraries, and other dependencies
RUN apt-get update && \
  apt-get install -y wget build-essential cmake libboost-all-dev git unzip &&\
  rm -rf /var/lib/apt/lists/*

# Install Python dependencies including pybind11
RUN pip3 install --no-cache-dir -r requirements.txt && \
  pip3 install pybind11

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

# Set pybind11_DIR environment variable
ENV pybind11_DIR="/usr/local/lib/python3.10/site-packages/pybind11/share/cmake/pybind11"

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

