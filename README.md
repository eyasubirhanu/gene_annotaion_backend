### Annotaion Service

backend API.

_Supported OS:_ **Linux & Mac**

**Follow these steps to run :**

## Prerequisites

- Docker
- Neo4j Aura account

## Setup

1. **Clone the Repository**

   ```sh
   git https://github.com/eyasubirhanu/gene_annotaion_backend.git
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
   Open app/routes.py and update database_type at line 28:

   - To use Metta, set database_type to 'metta'.
   - To use Neo4j, set database_type to 'cypher'.

Example

   ```python
   database_type = 'metta'  # Use 'cypher' for Neo4j
   ```

4. **Build and Run the Docker Container**

   Ensure you are in the root directory of the project and then run:

   ```sh
   docker build -t app .
   docker run app
   ```

   This will build the Docker image and run the container, exposing the application on port 5000.
