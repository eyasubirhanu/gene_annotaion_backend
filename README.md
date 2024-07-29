### Annotaion Service

backend API.

*Supported OS:* **Linux & Mac**

**Follow these steps to run :**

# My Neo4j Flask App

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

3. **Build and Run the Docker Container**

    Ensure you are in the root directory of the project and then run:

    ```sh
    docker build -t app .
    docker run app
    ```

    This will build the Docker image and run the container, exposing the application on port 5000.
    
