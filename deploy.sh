#!/bin/bash

echo "Stopping existing containers..."
docker-compose down --remove-orphans

echo "\nBuilding Docker images..."
docker-compose build

echo "\nStarting all services in detached mode..."
docker-compose up -d

echo "\nDeployment complete! Access services:
Frontend Dashboard: http://localhost:8050
Airflow UI: http://localhost:8080 (admin/admin)
Backend Health: http://localhost:5000/api/health"

# Display running containers
echo "Running containers:"
docker-compose ps

echo -e "\nApplication URLs:"
echo "- Airflow: http://localhost:8080 (admin/admin)"
echo "- Frontend Dashboard: http://localhost:8050"
echo "- Backend API: http://localhost:5000/api/health"

echo -e "\nMonitoring logs (press Ctrl+C to exit):"
docker-compose logs -f frontend backend 