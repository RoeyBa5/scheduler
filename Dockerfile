FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code
COPY . .

EXPOSE 8000
EXPOSE 8001

# Run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8001"]

