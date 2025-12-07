.PHONY: build start stop restart logs clean

build:
	@echo "Building and starting Docker containers..."
	docker compose up --build -d
	@echo "Build complete."

start:
	@echo "Starting Docker containers..."
	docker compose up -d
	@echo "Containers started."

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
	docker compose logs -f web

clean:
	@echo "Cleaning up unused Docker resources..."
	docker system prune -a --volumes -f
	@echo "Cleanup complete."
