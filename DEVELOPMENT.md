# 💻 Local Development Workflow

This document outlines the essential commands for setting up and working with the Dockerized environment locally. Since we are **not** using a centralized Docker Registry (Docker Hub), every collaborator must perform the initial build.

## 1. 🚀 Initial Setup: Build & Run

Run this command **once** when starting the project for the first time, or whenever you modify the **`Dockerfile`** or **`requirements.txt`**.

This process handles the large dependencies and ensures the server is running in the background.

```bash
make build
```

## 2. 🌐 Access the Application

Once the containers are successfully started, the application is accessible via your browser at the following address:

```
http://localhost:5000
```

## 3. ⏯️ Start Project (After **`down`**)
If the project was stopped using **`docker compose down`**, use this command to start the containers again without rebuilding the image.

```bash
make start
```

## 4. 🔄 Daily Workflow (Code Changes)

When you modify the application code (Python, HTML, etc.), **no command is necessary**. The Gunicorn server has been configured with the `--reload` flag, which automatically detects changes in your local source code (due to the volume mount) and restarts the application workers instantly.

**Simply save your file, and refresh your browser.**

If the automatic reload fails to detect changes, use this command to force a restart of the web service:

```bash
make restart
```

## 5. 🛑 Shut Down the Project

To stop and remove the running containers and network (while keeping the persistent database data volume):

```bash
make stop
```
