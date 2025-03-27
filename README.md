## ORSI Video API
This API allows users to upload videos, process them using AI models, and manage the videos by fetching, deleting, and retrieving metadata. The application is built using FastAPI and provides endpoints for handling video uploads, metadata retrieval, and video management. 
The AI processing is done asynchronously in a separate thread to ensure that video uploads don't block the server.

## Table of Contents

1. Installation

2. API Endpoints
   - POST /upload/
   - GET /videos/
   - GET /videos/{filename}
   - DELETE /videos/{filename}
   - GET /videos/{filename}/metadata

3. Running the Server

### Installation

To get started with the project, clone the repository and install the dependencies.
### Step 1: Clone the repository

`git clone https://github.com/your-username/video-ai-api.git`

`cd video-ai-api`

### Step 2: Install dependencies

Make sure you have Python 3.7+ installed. Then, install the required packages using pip.

`pip install -r requirements.txt`

### API Endpoints
* #### POST /upload/

   Uploads a video file to the server, processes it asynchronously with AI, and stores the processed metadata in the results folder.
   
   Request
   
   `POST /upload/
   Content-Type: multipart/form-data
   Body: { video file }`
   
   Response
   
   `{
   "filename": "example.mp4",
   "message": "Video uploaded successfully"
   }`

* #### GET /videos/

   Fetches a list of all uploaded videos.
   `Request GET /videos/`
   
   `Response
   {
   "videos": ["video1.mp4", "video2.mp4", "video3.mp4"]
   }`

* #### GET /videos/{filename}

   Fetches a specific video by filename.
   Request
   
   `GET /videos/{filename}`
   
   Example Response (video served as file download)
   
   The video file will be returned as a response to be played in the browser or downloaded.

* #### DELETE /videos/{filename}

   Deletes a specific video by filename.
   Request
   
   `DELETE /videos/{filename}`
   
   `Response
   {"message": "'example.mp4' deleted successfully"}`

* #### GET /videos/{filename}/metadata

   Fetches the metadata associated with a specific video, which includes AI-processed key moments, if available.
   Request

* #### GET /videos/{filename}/metadata

   Response
   
   `{
   "key_moments": [
   {
   "time": "00:00:00",
   "text": "The video begins; the opening frame is displayed. The speaker introduces the concept of 'agent' AI as the next big innovation."
   },
   {
   "time": "00:00:05",
   "text": "Visual: A comparison of traditional AI assistants with the described 'agent' AI is presented. The speaker contrasts traditional AI with the autonomous capabilities of 'agent' AI."
   }
   // More key moments...
   ]
   }`

### Running the Server

To run the server locally:

- Ensure you have all the dependencies installed.

- Run the FastAPI server using uvicorn.

`  uvicorn app:app --host 0.0.0.0 --port 8000`

The server will start on http://127.0.0.1:8000.
The Swagger UI can be accessed at http://127.0.0.1:8000/docs to interact with the API

### NOTES
* videos/: This folder contains all uploaded videos.

* results/: This folder stores metadata files related to processed videos (JSON files).

* To test this api, there is a **`video file into videos`** folder, you can upload it from UI

### Running with Docker

1. Build the Docker Image

    `docker build -t my-fastapi-app .`

2. Run the Container

    `docker run -p 8000:8000 my-fastapi-app`
