FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /opt

# Install dependencies
RUN apt-get update && apt-get install -y \
    cmake \
    make \
    g++ \
    wget \
    libboost-all-dev \
    unzip

COPY ./annotation_graph /opt/annotation_graph

# Install OGDF
WORKDIR /opt/annotation_graph/OGDF
RUN cmake . \
    && make -j4 \
    && make install

# Install RapidJSON by copying headers to the appropriate location
RUN cp -r /opt/annotation_graph/rapidjson-1.1.0/include/rapidjson /usr/local/include/
# Install Pybind11 using pip
RUN pip3 install pybind11[global]

WORKDIR /opt/annotation_graph/annotation-graph
RUN mkdir build && cd build && cmake .. && make -j4 && make install 

# Cleanup
RUN rm -rf /opt/annotation_graph

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
