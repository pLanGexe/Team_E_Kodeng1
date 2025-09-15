# SWE4ME-3-Tiers

A 3-tier architecture project setup with DevContainer support for consistent development environments.

## 🚀 Quick Start with DevContainers

This project is configured to work seamlessly with Visual Studio Code DevContainers, providing a consistent development environment across different machines.

### Prerequisites

- [Visual Studio Code](https://code.visualstudio.com/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine

### Getting Started

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd swe4me-3tiers
   ```

2. **Open in DevContainer:**
   - Open the project in VS Code
   - When prompted, click "Reopen in Container" 
   - Or use Command Palette (`Ctrl+Shift+P`) → "Dev Containers: Reopen in Container"

3. **Wait for container setup:**
   - The DevContainer will automatically build and configure your environment
   - This may take a few minutes on first run

## 🏗️ DevContainer Configuration

### Container Architecture

The DevContainer setup uses Docker Compose with the following configuration:

- **Base Image:** `mcr.microsoft.com/devcontainers/base:bullseye` (Debian Bullseye)
- **Service Name:** `app`
- **Workspace Location:** `/workspaces/swe4me-3tiers`

### Installed Tools & Features

#### Base Environment
- **Python 3** with pip and venv support
- **curl** for HTTP requests
- **Docker-outside-of-Docker** feature enabled

#### Docker Integration
- Docker socket forwarding from host to container
- Non-root Docker access enabled
- Moby engine support

### Environment Variables

The container sets the following Python environment variables:
- `PYTHONDONTWRITEBYTECODE=1` - Prevents Python from writing .pyc files
- `PYTHONUNBUFFERED=1` - Ensures Python output is sent straight to terminal

### Volume Mounts

- **Docker Socket:** `/var/run/docker.sock:/var/run/docker-host.sock`
  - Enables Docker commands inside the container
- **Workspace:** `../..:/workspaces:cached`
  - Mounts your project files with cached performance optimization

## 🔧 Development Workflow

### Quick Setup Verification

After opening the project in DevContainer, verify your setup with these one-liners:

```bash
# Test library installation
python3 -c "import fastapi, streamlit, sqlalchemy; print('Libraries installed successfully!')"

# Test database connection (ensure PostgreSQL container is running)
python3 -c "
import sys; sys.path.append('.')
from backend.db import init_db, increment_and_get
init_db()
print('Database test - Counter value:', increment_and_get()[0])
print('Database test - Counter value:', increment_and_get()[0])
"
```

### Working with Docker

Since Docker-outside-of-Docker is enabled, you can run Docker commands directly inside the DevContainer:

```bash
# Check Docker version
docker --version

# Build and run containers
docker-compose up -d

# View running containers
docker ps
```

### Python Development

The container comes with Python 3 pre-installed:

```bash
# Install dependencies
pip install -r requirements.txt

# Run your application
python3 app.py
```

### Port Forwarding

To expose application ports, uncomment and configure the `forwardPorts` setting in `.devcontainer/devcontainer.json`:

```json
"forwardPorts": [3000, 8080, 5432]
```

## 📁 Project Structure

```
swe4me-3tiers/
├── .devcontainer/
│   ├── devcontainer.json    # DevContainer configuration
│   ├── Dockerfile          # Container image definition
│   └── docker-compose.yml  # Multi-container setup
├── README.md               # This file
└── [your application files]
```

## 🛠️ Customization

### Adding New Tools

To install additional packages, modify `.devcontainer/Dockerfile`:

```dockerfile
RUN apt-get update && apt-get install -y \
    your-package-here \
    another-package \
    && rm -rf /var/lib/apt/lists/*
```

### Post-Creation Commands

Add commands to run after container creation in `devcontainer.json`:

```json
"postCreateCommand": "pip install -r requirements.txt"
```

### VS Code Extensions

Add extensions that should be installed in the container:

```json
"customizations": {
    "vscode": {
        "extensions": [
            "ms-python.python",
            "ms-python.flake8"
        ]
    }
}
```

## 🐛 Troubleshooting

### Container Won't Start
- Ensure Docker is running on your host machine
- Check Docker Desktop settings for WSL2 integration (Windows users)
- Verify no port conflicts with existing services

### Docker Commands Fail
- Confirm Docker socket is properly mounted
- Check that your user has Docker permissions on the host

### Slow Performance
- Consider adjusting volume mount cache settings
- Ensure adequate resources allocated to Docker

## 📚 Additional Resources

- [DevContainers Documentation](https://containers.dev/)
- [VS Code DevContainers Guide](https://code.visualstudio.com/docs/devcontainers/containers)
- [Docker Compose Reference](https://docs.docker.com/compose/)

## 🤝 Contributing

When contributing to this project:

1. Ensure your changes work within the DevContainer environment
2. Update this README if you modify the DevContainer configuration
3. Test the setup on a fresh container build

---

**Happy coding! 🎉**