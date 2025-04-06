# DockerForge Deployment Guides

This document provides detailed instructions for deploying DockerForge in various environments, from single-user development setups to enterprise production deployments.

## Table of Contents

- [Basic Deployment (Single User)](#basic-deployment-single-user)
- [Docker-based Deployment](#docker-based-deployment)
- [Production Deployment](#production-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Enterprise Deployment](#enterprise-deployment)

## Basic Deployment (Single User)

This is the simplest deployment method, suitable for individual developers or small teams.

### Prerequisites

- Python 3.8 or newer
- Docker Engine installed and running
- pip (Python package manager)

### Installation Steps

1. **Install DockerForge using pip:**

   ```bash
   pip install dockerforge
   ```

2. **Start DockerForge:**

   ```bash
   dockerforge start
   ```

3. **Access the web interface:**

   Open your browser and navigate to `http://localhost:8080`

4. **Complete the setup wizard:**

   Follow the on-screen instructions to complete the initial setup.

### Configuration

The default configuration is stored in `~/.dockerforge/config.yaml`. You can edit this file to customize your installation:

```yaml
server:
  host: 0.0.0.0
  port: 8080
  debug: false

docker:
  socket: /var/run/docker.sock
  # For remote Docker:
  # host: tcp://remote-docker-host:2375
  # tls: true
  # cert_path: ~/.docker/certs

database:
  type: sqlite
  path: ~/.dockerforge/data/dockerforge.db

logging:
  level: info
  path: ~/.dockerforge/logs
```

## Docker-based Deployment

Running DockerForge in a Docker container provides better isolation and easier updates.

### Prerequisites

- Docker Engine installed and running
- Docker Compose (optional, but recommended)

### Using Docker Run

1. **Pull the DockerForge image:**

   ```bash
   docker pull dockerforge/dockerforge:latest
   ```

2. **Run the container:**

   ```bash
   docker run -d \
     --name dockerforge \
     -p 8080:8080 \
     -v /var/run/docker.sock:/var/run/docker.sock \
     -v dockerforge_data:/data \
     dockerforge/dockerforge:latest
   ```

3. **Access the web interface:**

   Open your browser and navigate to `http://localhost:8080`

### Using Docker Compose

1. **Create a docker-compose.yml file:**

   ```yaml
   version: '3'
   services:
     dockerforge:
       image: dockerforge/dockerforge:latest
       container_name: dockerforge
       ports:
         - "8080:8080"
       volumes:
         - /var/run/docker.sock:/var/run/docker.sock
         - dockerforge_data:/data
       restart: unless-stopped
   
   volumes:
     dockerforge_data:
   ```

2. **Start the services:**

   ```bash
   docker-compose up -d
   ```

3. **Access the web interface:**

   Open your browser and navigate to `http://localhost:8080`

## Production Deployment

For production environments, consider these additional configurations for security, reliability, and performance.

### Prerequisites

- Docker Engine in Swarm mode or Kubernetes
- PostgreSQL database (recommended for production)
- Reverse proxy (Nginx, Traefik, etc.)
- TLS certificates

### PostgreSQL Setup

1. **Create a PostgreSQL database:**

   ```sql
   CREATE DATABASE dockerforge;
   CREATE USER dockerforge WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE dockerforge TO dockerforge;
   ```

2. **Update DockerForge configuration to use PostgreSQL:**

   ```yaml
   database:
     type: postgresql
     host: postgres.example.com
     port: 5432
     name: dockerforge
     user: dockerforge
     password: secure_password
     ssl: true
   ```

### Reverse Proxy Configuration

#### Nginx Example

```nginx
server {
    listen 80;
    server_name dockerforge.example.com;
    
    # Redirect HTTP to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name dockerforge.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Docker Swarm Deployment

1. **Create a docker-compose.yml file for Swarm:**

   ```yaml
   version: '3.8'
   
   services:
     dockerforge:
       image: dockerforge/dockerforge:latest
       ports:
         - "8080:8080"
       volumes:
         - /var/run/docker.sock:/var/run/docker.sock
         - dockerforge_data:/data
       environment:
         - DB_TYPE=postgresql
         - DB_HOST=postgres
         - DB_PORT=5432
         - DB_NAME=dockerforge
         - DB_USER=dockerforge
         - DB_PASSWORD=secure_password
       deploy:
         replicas: 1
         restart_policy:
           condition: on-failure
         update_config:
           order: start-first
           failure_action: rollback
       networks:
         - dockerforge_net
   
     postgres:
       image: postgres:14
       volumes:
         - postgres_data:/var/lib/postgresql/data
       environment:
         - POSTGRES_DB=dockerforge
         - POSTGRES_USER=dockerforge
         - POSTGRES_PASSWORD=secure_password
       deploy:
         replicas: 1
         restart_policy:
           condition: on-failure
       networks:
         - dockerforge_net
   
   volumes:
     dockerforge_data:
     postgres_data:
   
   networks:
     dockerforge_net:
   ```

2. **Deploy the stack:**

   ```bash
   docker stack deploy -c docker-compose.yml dockerforge
   ```

## Cloud Deployment

DockerForge can be deployed on various cloud platforms. Here are guides for the most common ones.

### AWS Deployment

1. **Launch an EC2 instance:**
   - Amazon Linux 2 or Ubuntu Server 20.04 LTS
   - t3.medium or larger (2 vCPU, 4 GB RAM minimum)
   - At least 20 GB EBS storage

2. **Install Docker:**

   ```bash
   # For Amazon Linux 2
   sudo yum update -y
   sudo amazon-linux-extras install docker
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker ec2-user
   
   # For Ubuntu
   sudo apt update
   sudo apt install -y docker.io
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker ubuntu
   ```

3. **Install DockerForge:**

   Follow the Docker-based deployment instructions above.

4. **Configure Security Groups:**
   - Allow inbound traffic on port 8080 (or your configured port)
   - Restrict access to trusted IP addresses

### Google Cloud Platform

1. **Create a Compute Engine VM:**
   - Ubuntu 20.04 LTS
   - e2-medium or larger (2 vCPU, 4 GB RAM minimum)
   - At least 20 GB persistent disk

2. **Install Docker and DockerForge:**

   Follow the same installation steps as for AWS.

3. **Configure Firewall Rules:**
   - Allow incoming traffic on port 8080

### Azure Deployment

1. **Create a Virtual Machine:**
   - Ubuntu Server 20.04 LTS
   - Standard_B2s or larger (2 vCPU, 4 GB RAM minimum)
   - At least 20 GB storage

2. **Install Docker and DockerForge:**

   Follow the same installation steps as for AWS.

3. **Configure Network Security Group:**
   - Allow incoming traffic on port 8080

## Enterprise Deployment

For enterprise environments with high availability and security requirements.

### High Availability Setup

1. **Database Cluster:**
   - Use a PostgreSQL cluster with replication
   - Consider managed database services (RDS, Cloud SQL, etc.)

2. **Load Balancing:**
   - Deploy multiple DockerForge instances
   - Use a load balancer (ELB, GCP Load Balancer, etc.)
   - Configure session persistence

3. **Shared Storage:**
   - Use a shared filesystem for data that needs to be consistent across instances
   - Consider NFS, EFS, or other distributed storage solutions

### Security Hardening

1. **Authentication:**
   - Configure LDAP or OAuth integration
   - Implement multi-factor authentication
   - Use strong password policies

2. **Network Security:**
   - Place DockerForge behind a VPN or in a private network
   - Implement IP whitelisting
   - Use Web Application Firewall (WAF)

3. **Docker Security:**
   - Use Docker Content Trust for image verification
   - Implement container security scanning
   - Apply principle of least privilege for container permissions

### Monitoring and Logging

1. **Monitoring Setup:**
   - Integrate with Prometheus for metrics
   - Set up Grafana dashboards
   - Configure alerts for critical events

2. **Centralized Logging:**
   - Forward logs to ELK stack or similar
   - Implement log retention policies
   - Set up log analysis for security events

### Backup Strategy

1. **Regular Backups:**
   - Database backups (daily or more frequent)
   - Configuration backups
   - Volume data backups

2. **Backup Verification:**
   - Regularly test restore procedures
   - Validate backup integrity

3. **Disaster Recovery:**
   - Document recovery procedures
   - Implement cross-region replication for critical data
   - Conduct disaster recovery drills

## Next Steps

After deploying DockerForge, refer to the [Post-Installation Guide](./post_installation.md) for:

- Initial configuration
- User setup
- Security best practices
- Performance tuning
