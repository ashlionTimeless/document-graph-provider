# Document Graph Provider

This project provides a service to convert documents into a graph structure and enables querying using advanced retrieval techniques. It uses Neo4j as the graph database and supports vector-based search with LlamaIndex.

## Features

- Upload documents and convert them into a graph structure.
- Query documents using advanced retrieval and embedding models.
- REST API built with Flask.
- Docker support for easy deployment.

## Requirements

- Python 3.10+
- Neo4j database (cloud or local)
- OpenAI API key (for embeddings)
- Docker (optional, for containerized deployment)

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Flask server port
PORT=6000

# Neo4j connection
NEO4J_URI=bolt://<your-neo4j-host>:7687
NEO4J_USERNAME=<your-neo4j-username>
NEO4J_PASSWORD=<your-neo4j-password>
NEO4J_DATABASE=neo4j

# Root directory for graph data
MS_GRAPHRAG_ROOT=/absolute/path/to/your/data

# OpenAI API Key (required for embedding)
OPENAI_API_KEY=sk-...
```

## Local Deployment

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd document-graph-provider
   ```

2. **Install dependencies:**
   ```bash
   pip install -U pip setuptools numpy
   pip install graphrag dotenv flask neo4j llama_index neo4j-driver pandas
   pip install llama-index-vector-stores-postgres llama-index-graph-stores-neo4j llama-index llama-index-vector-stores-neo4jvector
   ```

3. **Set up your `.env` file** as described above.

4. **Run the server:**
   ```bash
   python src/index.py
   ```

   The server will start on the port specified in your `.env` file (default: 6000).

## Docker Deployment

1. **Build the Docker image:**
   ```bash
   docker build -t document-graph-provider .
   ```

2. **Run the container:**
   ```bash
   docker run --env-file .env -p 6000:6000 document-graph-provider
   ```

   Make sure your `.env` file is present in the project root and contains all required variables.

## API Endpoints

### `POST /upload-document`
- **Body:**
  ```json
  { "document_id": "<folder-or-document-id>" }
  ```
- **Description:** Uploads and processes a document/folder into the graph.
- **Example using curl:**
  ```bash
  curl -X POST http://localhost:6000/upload-document \
    -H "Content-Type: application/json" \
    -d '{"document_id": "example_folder"}'
  ```

### `POST /query-document`
- **Body:**
  ```json
  { "document_id": "<folder-or-document-id>", "query": "<your-query>" }
  ```
- **Description:** Queries the processed document graph.
- **Example using curl:**
  ```bash
  curl -X POST http://localhost:6000/query-document \
    -H "Content-Type: application/json" \
    -d '{"document_id": "example_folder", "query": "What are the main entities?"}'
  ```

## Data Preparation

- Place your document data in the directory specified by `MS_GRAPHRAG_ROOT`.
- The expected structure is:
  ```
  MS_GRAPHRAG_ROOT/
    <document_id>/
      output/
        documents.parquet
        text_units.parquet
        entities.parquet
        embeddings.entity.description.parquet
        relationships.parquet
        communities.parquet
        community_reports.parquet
  ```

## License

This project is licensed under the Apache 2.0 License. 