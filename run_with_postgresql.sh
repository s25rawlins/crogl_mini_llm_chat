#!/bin/bash
# Script to run Mini LLM Chat with PostgreSQL backend

# Set the DATABASE_URL to use local socket connection
export DATABASE_URL="postgresql:///mini_llm_chat"

# Run the application with PostgreSQL backend
python -m mini_llm_chat.cli --db-backend postgresql "$@"
