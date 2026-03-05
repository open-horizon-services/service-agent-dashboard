# Service Agent Dashboard

A lightweight Docker container monitoring dashboard designed for resource-constrained edge IoT devices. This application provides a real-time web interface to monitor all running Docker containers on a machine with minimal resource overhead.

## Features

- 🚀 **Lightweight**: Built with Alpine Linux base image (~50MB total)
- 📊 **Real-time Monitoring**: Auto-refreshes every 5 seconds
- 💻 **Resource Efficient**: Optimized for edge IoT devices with limited CPU/memory
- 🐳 **Container Stats**: CPU usage, memory usage, status, ports, and more
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🔒 **Secure**: Runs as non-root user, read-only Docker socket access

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone or navigate to the project directory
cd service-agent-dashboard

# Build and start the dashboard
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the dashboard
docker-compose down
```

The dashboard will be available at: http://localhost:5000

### Using Docker CLI

```bash
# Build the image
docker build -t service-agent-dashboard .

# Run the container (with proper Docker socket permissions)
docker run -d \
  --name service-agent-dashboard \
  -p 5000:5000 \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  --user root \
  --restart unless-stopped \
  service-agent-dashboard

# Alternative: Run with docker group permissions (more secure)
# docker run -d \
#   --name service-agent-dashboard \
#   -p 5000:5000 \
#   -v /var/run/docker.sock:/var/run/docker.sock:ro \
#   --group-add $(getent group docker | cut -d: -f3) \
#   --user 1000:$(getent group docker | cut -d: -f3) \
#   --restart unless-stopped \
#   service-agent-dashboard
```

### Using Pre-built Image

```bash
# If you've pushed to a registry
docker run -d \
  --name service-agent-dashboard \
  -p 5000:5000 \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  --restart unless-stopped \
  your-registry/service-agent-dashboard:latest
```

## Resource Requirements

### Minimum Requirements (IoT Edge Devices)
- **CPU**: 0.1 cores (10% of one CPU)
- **Memory**: 64 MB
- **Disk**: ~50 MB for Docker image

### Recommended for Production
- **CPU**: 0.5 cores (50% of one CPU)
- **Memory**: 128 MB
- **Disk**: ~50 MB for Docker image

The docker-compose.yml includes resource limits suitable for constrained environments.

## Configuration

### Port Configuration
Change the port mapping in `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Change 8080 to your desired port
```

### Resource Limits
Adjust resource limits in `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'      # Maximum CPU usage
      memory: 128M     # Maximum memory
    reservations:
      cpus: '0.1'      # Minimum CPU reservation
      memory: 64M      # Minimum memory reservation
```

## API Endpoints

The dashboard exposes the following REST API endpoints:

- `GET /` - Web dashboard interface
- `GET /api/containers` - List all containers with details and stats
- `GET /api/system` - Docker system information

### Example API Usage

```bash
# Get all containers
curl http://localhost:5000/api/containers

# Get system info
curl http://localhost:5000/api/system
```

## Dashboard Features

### System Overview
- Total containers count
- Running/stopped containers
- Total images
- CPU and memory information

### Container Details
- Container ID and name
- Image name and tag
- Current status (running, stopped, paused)
- Port mappings
- Creation timestamp
- Real-time CPU usage percentage
- Real-time memory usage and limits

### Visual Indicators
- Color-coded status badges
- Progress bars for CPU and memory usage
- High usage warnings (>80% turns red)

## Security Considerations

1. **Read-only Docker Socket**: The Docker socket is mounted as read-only (`:ro`)
2. **Non-root User**: Container runs as non-root user (UID 1000)
3. **Minimal Attack Surface**: Alpine Linux base with minimal packages
4. **No External Dependencies**: All assets served from the container

## Troubleshooting

### Dashboard not accessible
```bash
# Check if container is running
docker ps | grep service-agent-dashboard

# Check logs
docker logs service-agent-dashboard

# Verify port is not in use
netstat -an | grep 5000
```

### Cannot connect to Docker daemon
Ensure the Docker socket is properly mounted:
```bash
# Check socket permissions
ls -la /var/run/docker.sock

# Verify socket is accessible in container
docker exec service-agent-dashboard ls -la /var/run/docker.sock
```

### High resource usage
If the dashboard uses too many resources:
1. Increase refresh interval in `templates/index.html` (change `5000` to `10000` for 10 seconds)
2. Reduce resource limits in `docker-compose.yml`
3. Disable stats collection by modifying the API endpoint

## Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (requires Docker daemon)
python app.py

# Access at http://localhost:5000
```

### Building for Different Architectures
```bash
# For ARM devices (Raspberry Pi, etc.)
docker buildx build --platform linux/arm64 -t service-agent-dashboard:arm64 .

# For AMD64
docker buildx build --platform linux/amd64 -t service-agent-dashboard:amd64 .

# Multi-arch build
docker buildx build --platform linux/amd64,linux/arm64 -t service-agent-dashboard:latest .
```

## Project Structure

```
service-agent-dashboard/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Multi-stage Docker build
├── docker-compose.yml    # Docker Compose configuration
├── README.md            # This file
└── templates/
    └── index.html       # Web dashboard UI
```

## Technology Stack

- **Backend**: Python 3.11 + Flask (minimal web framework)
- **Docker API**: docker-py library
- **Frontend**: Vanilla JavaScript (no frameworks)
- **Base Image**: Alpine Linux 3.x (minimal footprint)

## License

This project is provided as-is for monitoring Docker containers on edge devices.

## Contributing

Feel free to submit issues and enhancement requests!

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Docker logs: `docker logs service-agent-dashboard`
3. Verify Docker socket permissions
4. Ensure Docker daemon is running

## Performance Tips

1. **Reduce Refresh Rate**: Modify the JavaScript interval in `index.html`
2. **Limit Container Stats**: Only collect stats for running containers
3. **Use Resource Limits**: Always set CPU and memory limits in production
4. **Monitor Dashboard**: Use the dashboard to monitor itself!

## Future Enhancements

Potential improvements for future versions:
- Container start/stop/restart controls
- Log viewing capability
- Historical metrics and graphs
- Alert notifications
- Multi-host support
- Authentication/authorization