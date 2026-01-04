FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# copy project
WORKDIR /app
COPY . /app

# install python deps
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# default command runs both FastAPI and Streamlit
EXPOSE 8000 8501
CMD ["/bin/bash", "-lc", "uvicorn agent_api:app --host 0.0.0.0 --port 8000 & streamlit run ultimate_research_agent.py --server.port 8501 --server.address 0.0.0.0"]
