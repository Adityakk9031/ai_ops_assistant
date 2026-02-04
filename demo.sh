#!/bin/bash

# Demo script for AI Operations Assistant
# This script demonstrates the complete workflow with example tasks

BASE_URL="http://localhost:8000"

echo "=== AI Operations Assistant Demo ==="
echo ""
echo "This demo will execute several example tasks to showcase the system."
echo "Make sure the server is running (python main.py) before continuing."
echo ""
read -p "Press Enter to start the demo..."

echo ""
echo "========================================="
echo "Demo 1: GitHub Repository Search"
echo "========================================="
echo ""
echo "Task: Find top 3 Python web frameworks on GitHub with > 5k stars"
echo ""

curl -X POST "$BASE_URL/api/submit" \
  -H "Content-Type: application/json" \
  -d '{"task":"Find top 3 Python web frameworks on GitHub with more than 5000 stars"}' \
  | python -m json.tool

echo ""
read -p "Press Enter to continue to next demo..."

echo ""
echo "========================================="
echo "Demo 2: Weather Query"
echo "========================================="
echo ""
echo "Task: Get current weather in Bangalore"
echo ""

curl -X POST "$BASE_URL/api/submit" \
  -H "Content-Type: application/json" \
  -d '{"task":"Get the current weather in Bangalore"}' \
  | python -m json.tool

echo ""
read -p "Press Enter to continue to next demo..."

echo ""
echo "========================================="
echo "Demo 3: Multi-Tool Task"
echo "========================================="
echo ""
echo "Task: Find top 3 Python web frameworks on GitHub and weather in Bangalore"
echo ""

curl -X POST "$BASE_URL/api/submit" \
  -H "Content-Type: application/json" \
  -d '{"task":"Find top 3 Python web frameworks on GitHub with > 5k stars and current weather in Bangalore, then create a summary"}' \
  | python -m json.tool

echo ""
echo "========================================="
echo "Demo Complete!"
echo "========================================="
echo ""
echo "You can try your own tasks by running:"
echo ""
echo "curl -X POST $BASE_URL/api/submit \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"task\":\"YOUR TASK HERE\"}' \\"
echo "  | python -m json.tool"
echo ""
