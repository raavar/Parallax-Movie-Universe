.PHONY: build_project build_with_live_logs database update_movies remove_csv_duplicates start stop restart logs clean

build_project:
	@echo "Building and starting Docker containers in detached mode..."
	docker compose up --build -d
	@echo "Build complete."

build_with_live_logs:
	@echo "Building and starting Docker containers..."
	docker compose up --build

database:
	@echo "Initializing the database with movie data..."
	docker compose run --rm web python3 database/populate_database.py
	docker compose run --rm web python3 database/update_metadata.py
	@echo "Database initialization complete."

create_global_server:
	make clean
	
	@echo "Creating the global server accessible from everywhere..."
	chmod +x allow_docker_database.bash
	./allow_docker_database.bash

	make build_project
	@echo "Waiting 10 seconds for Database to initialize..."
	@sleep 10
	
	make database
	make start
	@echo "Global server created successfully."

update_movies:
	@echo "Updating movie metadata..."
	docker compose run --rm web python3 database/update_metadata.py
	@echo "Movie metadata update complete."

remove_csv_duplicates:
	@echo "Removing duplicate entries from movies.csv and movies_without_poster.csv..."
	docker compose run --rm web python3 database/remove_csv_duplicates.py
	@echo "Duplicate removal complete."

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
	docker compose logs web > logs.txt

clean:
	@echo "Cleaning up unused Docker resources..."
	docker compose down -v --rmi local --remove-orphans
	@echo "Cleanup complete."
