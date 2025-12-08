.PHONY: detached_build build start database stop restart logs clean

detached_build:
	@echo "Building and starting Docker containers in detached mode..."
	docker compose up --build -d
	@echo "Build complete."

build:
	@echo "Building and starting Docker containers..."
	docker compose up --build

start:
	@echo "Starting Docker containers..."
	docker compose up -d
	@echo "Containers started."

database:
	@echo "Initializing the database with movie data..."
	docker compose run --rm web python3 populate_database.py
	@echo "Database initialization complete."

stop:
	@echo "Stopping Docker containers..."
	docker compose down
	@echo "Containers stopped."
	
restart:
	@echo "Restarting web container..."
	docker compose restart web
	@echo "Web container restarted."

logs:
	@echo "Showing logs for web container..."
	docker compose logs web > logs.txt

clean:
	@echo "Cleaning up unused Docker resources..."
	docker system prune -a --volumes -f
	@echo "Cleanup complete."
