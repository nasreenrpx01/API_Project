# FastAPI-based Content Processing and Retrieval API

## Overview
This project is a FastAPI-based API designed for processing and retrieving content from URLs and PDF files. The API utilizes advanced text embedding techniques powered by SentenceTransformer for semantic search and similarity scoring. The application is containerized using Docker for ease of deployment and scalability.

## Features
- **Content Processing**: Extracts and processes content from URLs and PDF files.
- **Semantic Search**: Provides semantic similarity-based responses for user queries.
- **Chunking**: Splits large text into smaller chunks for efficient embedding.
- **Real-time Query Handling**: Supports dynamic querying of processed content.
- **Scalable Deployment**: Uses Docker for seamless deployment with a multi-container setup.

## Endpoints
### 1. `GET /`
- **Description**: Health check endpoint to confirm the server is running.
- **Response**: `{ "message": "FastAPI server is running successfully!" }`

### 2. `POST /process_url`
- **Description**: Processes a given URL and extracts content.
- **Request**:
  ```json
  {
      "url": "<URL to process>"
  }
  ```
- **Response**:
  ```json
  {
      "chat_id": "<Unique ID>",
      "message": "URL content processed successfully."
  }
  ```

### 3. `POST /process_pdf`
- **Description**: Processes an uploaded PDF file and extracts content.
- **Request**: Upload a `.pdf` file.
- **Response**:
  ```json
  {
      "chat_id": "<Unique ID>",
      "message": "PDF content processed successfully."
  }
  ```

### 4. `POST /chat`
- **Description**: Queries the processed content based on the chat ID and question.
- **Request**:
  ```json
  {
      "chat_id": "<Unique ID>",
      "question": "<Query text>"
  }
  ```
- **Response**:
  ```json
  {
      "query": "<Query text>",
      "response": "<Relevant content>",
      "similarity": 0.85
  }
  ```

## Technologies Used
- **Framework**: FastAPI
- **Machine Learning**: SentenceTransformer
- **PDF Processing**: PyPDF2
- **Web Scraping**: BeautifulSoup
- **Containerization**: Docker
- **Database**: PostgreSQL

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/<your-username>/fastapi-docker-api.git
   cd fastapi-docker-api
   ```

2. **Create a `.env` File** (for PostgreSQL credentials):
   ```env
   POSTGRES_USER=user
   POSTGRES_PASSWORD=password
   POSTGRES_DB=app_data
   ```

3. **Build and Start Docker Containers**:
   ```bash
   docker-compose up --build
   ```

4. **Access the API**:
   Open your browser and navigate to `http://127.0.0.1:8000`.

## Docker Configuration
### `docker-compose.yml`
```yaml
version: '3.9'

services:
  api:
    image: python:3.9-slim
    container_name: fastapi-app
    working_dir: /app
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    command: sh -c "pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8000"

  db:
    image: postgres:15
    container_name: fastapi-db
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: app_data
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Usage
1. Use the `/process_url` endpoint to process content from a URL.
2. Use the `/process_pdf` endpoint to process content from a PDF file.
3. Use the `/chat` endpoint to query the processed content using the `chat_id`.

## Future Improvements
- Add support for additional file formats (e.g., DOCX).
- Integrate advanced NLP models for deeper analysis.
- Implement user authentication for enhanced security.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
