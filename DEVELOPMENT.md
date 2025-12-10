# 💻 Local Development Workflow

This document outlines the essential commands for setting up and working with the Dockerized environment locally. Since we are **not** using a centralized Docker Registry (Docker Hub), every collaborator must perform the initial build.

## 0. ⚙️ Before setup note

Before starting the setup you need to create the .env file with contents: `APP_SECRET_KEY`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_URL`.

## 1. 🚀 Initial Setup: Build & Run

Run this command **once** when starting the project for the first time, or whenever you modify the `Dockerfile` or `requirements.txt`.

This process handles the large dependencies and ensures the server is running in the background.

```bash
make detached_build
```

### 🛠️ Alternative: Interactive Build (Debug Mode)

If you are encountering errors during the build process or startup and need to **see the logs in real-time in your terminal**, use this command instead of the one above:

```bash
make build
```

**Note**: This runs in the foreground. Pressing `Ctrl+C` will stop the application.

## 2. 🗃️ Database Initialization

After the initial image build is complete, you must run the population script to create the database tables and load the initial movie data from movies.csv.

Run this command exactly once:

```bash
make database
```

## 3. 🌐 Access the Application

Once the containers are successfully started, the application is accessible via your browser at the following address:

```
http://localhost:5000
```

## 4. ⏯️ Start Project (After `stop`)
If the project was stopped using `make stop`, use this command to start the containers again without rebuilding the image.

```bash
make start
```

## 5. 🔄 Daily Workflow (Code Changes)

When you modify the application code (Python, HTML, etc.), **no command is necessary**. The Gunicorn server has been configured with the `--reload` flag, which automatically detects changes in your local source code (due to the volume mount) and **restarts** the application workers instantly.

**Simply save your file, and refresh your browser.**

**Note**: If the automatic reload fails to detect changes, use this command to force a restart of the web service:

```bash
make restart
```

## 6. 📝 Debugging & Logs

If the application crashes or behaves unexpectedly, you can dump the logs of the web container to a file named `logs.txt` for analysis:

```bash
make logs
```

## 7. 🛑 Shut Down the Project

To stop and remove the running containers and network (while keeping the persistent database data volume):

```bash
make stop
```

## 8. 🧹 Deep Clean (Factory Reset)

**WARNING**: Use this command only if you want to remove **everything** (containers, images, and volumes). This will **delete** your database data and require a full rebuild next time.

Useful for freeing up disk space or fixing corrupted Docker states.

```bash
make clean
```
