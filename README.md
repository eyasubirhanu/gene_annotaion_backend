### Annotation Service

Backend API.

_Supported OS:_ **Linux & Mac**

**Follow these steps to run:**

## Prerequisites

- Docker
- Neo4j Aura account

### If Not Using Docker:

- Python 3.10
- GCC or g++ compiler
- OGDF (Open Graph Drawing Framework)
- RapidJSON
- Pybind11 (installed via pip)

## Setup

1. **Clone the Repository**

   ```sh
   git clone https://github.com/eyasubirhanu/gene_annotaion_backend.git
   cd gene_annotaion_backend
   ```

2. **Create a `.env` File**

   Create a `.env` file at the root of the project directory with the following contents, replacing the placeholder values with your actual Neo4j credentials:

   ```env
   NEO4J_URI=<neo4j-url>
   NEO4J_USERNAME=<neo4j-username>
   NEO4J_PASSWORD=<neo4j-password>
   ```

3. **Choose Your Database Type**

   In the `config` directory, modify `config.ini` to switch between databases.

   - To use Metta, set the type to 'metta'.
   - To use Neo4j, set the type to 'cypher'.

   Example:

   ```ini   
   [database]
   type = cypher  # Change to 'metta' if needed
   ```

4. **If Using Docker: Build and Run the Docker Container**

   Ensure you are in the root directory of the project and then run:

   ```sh
   docker build -t app .
   docker run app
   ```

   This will build the Docker image and run the container, exposing the application on port 5000.

5. **If Not Using Docker: Install Dependencies and Build**

   a. **Install Python Dependencies**:

   Ensure you have Python 3.10 installed. Create and activate a virtual environment:

   ```sh
   python3.10 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

   b. **Install OGDF**:

   Download and install OGDF with `-fPIC` to ensure it's path-independent:

   ```sh
   wget https://ogdf.uos.de/wp-content/uploads/2020/02/ogdf.v2020.02.zip
   unzip ogdf.v2020.02.zip
   rm ogdf.v2020.02.zip
   cd OGDF
   mkdir build && cd build
   cmake -DCMAKE_POSITION_INDEPENDENT_CODE=ON ..
   make -j4
   sudo make install
   ```

   c. **Install RapidJSON**:

   Download and install RapidJSON:

   ```sh
   wget https://github.com/Tencent/rapidjson/archive/v1.1.0.tar.gz -O rapidjson.tar.gz
   tar -xzf rapidjson.tar.gz
   rm rapidjson.tar.gz
   sudo cp -r rapidjson-1.1.0/include/rapidjson /usr/local/include
   rm -rf rapidjson-1.1.0
   ```

   d. **Install Pybind11**:

   Install Pybind11 using pip:

   ```sh
   pip install pybind11
   ```

   e. **Build the `annotation-graph`**:

   Build the `annotation-graph` using the following commands:

   ```sh
   mkdir -p /app/annotation-graph/build
   cd /app/annotation-graph/build
   cmake -DCMAKE_POSITION_INDEPENDENT_CODE=ON ..
   make
   sudo make install
   ```

6. **Run the Application**

   Once all dependencies are installed and the `annotation-graph` is built, you can run the application:

   ```sh
   python run.py
   ```
