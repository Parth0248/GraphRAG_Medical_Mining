# Local Docker Deployment Guide

This guide provides step-by-step instructions for building and running the GraphRAG Medical Mining application locally using Docker.

## Prerequisites

- Docker installed on your system ([Install Docker](https://docs.docker.com/get-docker/))
- Git (to clone the repository)
- At least 4GB of available RAM
- Internet connection for downloading dependencies

## Quick Start

### 1. Clone the Repository (if not already done)

```bash
git clone https://github.com/Parth0248/GraphRAG_Medical_Mining.git
cd GraphRAG_Medical_Mining
```

### 2. Set Up Environment Variables

Before building the Docker image, you need to configure your API keys and database credentials.

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your credentials:
   ```bash
   # Groq API Key (FREE - https://console.groq.com)
   GROQ_API_KEY=gsk_your_key_here
   
   # Neo4j Database Credentials (FREE - https://neo4j.com/cloud/aura-free/)
   NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your_password
   ```

#### How to Get FREE API Keys:

**Groq API (FREE LLM):**
- Visit: https://console.groq.com
- Sign up (no credit card required)
- Create API Key
- Copy key (starts with `gsk_`)
- Free tier: 14,400 requests/day

**Neo4j Aura (FREE Graph Database):**
- Visit: https://neo4j.com/cloud/aura-free/
- Sign up
- Create free database
- Copy URI, username, password
- Free tier: 200MB storage

### 3. Build the Docker Image

Build the Docker image with the following command:

```bash
docker build -t graphrag-medical-mining .
```

This will:
- Use Python 3.10-slim as the base image
- Install all system dependencies (build tools, curl, git, libgomp1)
- Install Python dependencies from `requirements.txt`
- Copy all application code to `/app` in the container
- Set up the Streamlit application on port 8501

**Note:** The build process may take 5-10 minutes depending on your internet connection and system performance.

### 4. Run the Docker Container

Run the container with environment variables:

```bash
docker run -d \
  --name graphrag-app \
  -p 8501:8501 \
  --env-file .env \
  graphrag-medical-mining
```

**Explanation of flags:**
- `-d`: Run container in detached mode (background)
- `--name graphrag-app`: Assign a name to the container
- `-p 8501:8501`: Map port 8501 from container to host
- `--env-file .env`: Load environment variables from `.env` file

### 5. Access the Application

Once the container is running, open your web browser and navigate to:

```
http://localhost:8501
```

You should see the GraphRAG Medical AI interface.

## Docker Commands Reference

### View Container Logs

To view real-time logs from the running container:

```bash
docker logs -f graphrag-app
```

Press `Ctrl+C` to stop viewing logs (container continues running).

### Stop the Container

```bash
docker stop graphrag-app
```

### Start the Container Again

```bash
docker start graphrag-app
```

### Remove the Container

```bash
docker rm graphrag-app
```

### Remove the Image

```bash
docker rmi graphrag-medical-mining
```

### Rebuild After Code Changes

If you make changes to the code and want to rebuild:

```bash
docker stop graphrag-app
docker rm graphrag-app
docker build -t graphrag-medical-mining .
docker run -d --name graphrag-app -p 8501:8501 --env-file .env graphrag-medical-mining
```

## Alternative: Docker Compose (Optional)

For easier management, you can create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  graphrag-app:
    build: .
    container_name: graphrag-app
    ports:
      - "8501:8501"
    env_file:
      - .env
    restart: unless-stopped
```

Then use:
- `docker-compose up -d` - Start the application
- `docker-compose down` - Stop the application
- `docker-compose logs -f` - View logs

## Troubleshooting

### Port Already in Use

If port 8501 is already in use, map to a different port:

```bash
docker run -d --name graphrag-app -p 8502:8501 --env-file .env graphrag-medical-mining
```

Then access at: `http://localhost:8502`

### Container Exits Immediately

Check the logs to see what went wrong:

```bash
docker logs graphrag-app
```

Common issues:
- Missing or invalid environment variables
- Neo4j database not accessible
- Invalid Groq API key

### Out of Memory

If the build fails due to memory issues, try:

```bash
docker build --memory=4g -t graphrag-medical-mining .
```

### Permission Denied

On Linux, you may need to run Docker commands with `sudo`:

```bash
sudo docker build -t graphrag-medical-mining .
sudo docker run -d --name graphrag-app -p 8501:8501 --env-file .env graphrag-medical-mining
```

### Environment Variables Not Loading

Make sure your `.env` file exists and contains valid credentials. You can also pass environment variables directly:

```bash
docker run -d \
  --name graphrag-app \
  -p 8501:8501 \
  -e GROQ_API_KEY=your_key \
  -e NEO4J_URI=your_uri \
  -e NEO4J_USERNAME=neo4j \
  -e NEO4J_PASSWORD=your_password \
  graphrag-medical-mining
```

### Healthcheck Failing

The container includes a healthcheck that verifies Streamlit is responding. If unhealthy:

1. Check logs: `docker logs graphrag-app`
2. Ensure port 8501 is not blocked
3. Verify application started successfully

## Performance Optimization

### Using GPU (if available)

If you have an NVIDIA GPU and want to use it for faster processing:

1. Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
2. Modify `requirements.txt` to use `faiss-gpu` instead of `faiss-cpu`
3. Rebuild the image
4. Run with GPU support:

```bash
docker run -d \
  --name graphrag-app \
  --gpus all \
  -p 8501:8501 \
  --env-file .env \
  graphrag-medical-mining
```

## Application Entry Point

The default entry point is `deployment/streamlit/app_final.py`, which provides the full-featured Streamlit interface.

**Alternative entry points** (if you want to use a different app):

- `app.py` - Basic version
- `app_demo.py` - Demo version
- `app_enhanced.py` - Enhanced features
- `app_premium.py` - Premium version

To use a different entry point, modify the `CMD` line in the Dockerfile:

```dockerfile
CMD ["streamlit", "run", "deployment/streamlit/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Then rebuild the image.

## Production Deployment

For production deployments, consider:

1. **Cloud Deployment**: See `DEPLOYMENT_INSTRUCTIONS.txt` for Streamlit Cloud deployment
2. **Security**: Use Docker secrets or a secrets management service instead of `.env` files
3. **Scaling**: Use Kubernetes or Docker Swarm for multiple instances
4. **Monitoring**: Add logging and monitoring tools like Prometheus
5. **Reverse Proxy**: Use NGINX or Traefik in front of the container

## System Requirements

- **Minimum RAM**: 4GB
- **Recommended RAM**: 8GB+
- **Disk Space**: ~5GB (including Docker image and dependencies)
- **CPU**: 2+ cores recommended
- **Network**: Stable internet connection for API calls

## Support

For issues and questions:
- Check the main [README.md](README.md) for comprehensive documentation
- Review [DEPLOYMENT_INSTRUCTIONS.txt](DEPLOYMENT_INSTRUCTIONS.txt) for cloud deployment
- Open an issue on the GitHub repository
- Refer to [INDEX.md](INDEX.md) for project overview

## License

This project is licensed under the MIT License - see the LICENSE file for details.
