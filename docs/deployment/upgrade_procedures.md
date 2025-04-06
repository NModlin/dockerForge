# DockerForge Upgrade Procedures

This document outlines the procedures for upgrading DockerForge to newer versions across different deployment methods.

## Table of Contents

- [Before You Upgrade](#before-you-upgrade)
- [Upgrading Pip Installation](#upgrading-pip-installation)
- [Upgrading Docker Container Installation](#upgrading-docker-container-installation)
- [Upgrading Docker Compose Installation](#upgrading-docker-compose-installation)
- [Upgrading Production Deployments](#upgrading-production-deployments)
- [Troubleshooting Upgrade Issues](#troubleshooting-upgrade-issues)

## Before You Upgrade

Before performing any upgrade, follow these preparatory steps:

### 1. Check Release Notes

Always review the release notes for the new version to understand:
- Breaking changes
- New features
- Deprecated features
- Required configuration changes

Release notes are available at: [https://github.com/NModlin/dockerForge/releases](https://github.com/NModlin/dockerForge/releases)

### 2. Backup Your Data

Always create a backup before upgrading:

```bash
# For pip installation
cp -r ~/.dockerforge ~/.dockerforge.backup-$(date +%Y%m%d)

# For Docker volume backup
docker run --rm -v dockerforge_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/dockerforge-backup-$(date +%Y%m%d).tar.gz /data
```

### 3. Test in a Non-Production Environment

If possible, test the upgrade in a development or staging environment before applying to production.

## Upgrading Pip Installation

### Standard Upgrade

For installations done via pip:

```bash
# Stop DockerForge if it's running
dockerforge stop

# Upgrade the package
pip install --upgrade dockerforge

# Start DockerForge
dockerforge start
```

### Major Version Upgrades

For major version upgrades (e.g., 1.x to 2.x):

```bash
# Stop DockerForge
dockerforge stop

# Create a backup
cp -r ~/.dockerforge ~/.dockerforge.backup-$(date +%Y%m%d)

# Uninstall old version
pip uninstall -y dockerforge

# Install new version
pip install dockerforge

# Start DockerForge
dockerforge start
```

After upgrading, check the web interface for any migration or setup wizards that need to be completed.

## Upgrading Docker Container Installation

### Using Latest Tag

If you're using the `latest` tag:

```bash
# Pull the new image
docker pull dockerforge/dockerforge:latest

# Stop and remove the current container
docker stop dockerforge
docker rm dockerforge

# Start a new container with the same configuration
docker run -d \
  --name dockerforge \
  -p 8080:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v dockerforge_data:/data \
  dockerforge/dockerforge:latest
```

### Using Specific Version Tags

If you're using specific version tags:

```bash
# Pull the new version
docker pull dockerforge/dockerforge:2.1.0  # Replace with your target version

# Stop and remove the current container
docker stop dockerforge
docker rm dockerforge

# Start a new container with the updated image
docker run -d \
  --name dockerforge \
  -p 8080:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v dockerforge_data:/data \
  dockerforge/dockerforge:2.1.0  # Replace with your target version
```

## Upgrading Docker Compose Installation

### Using Latest Tag

If your docker-compose.yml uses the `latest` tag:

```bash
# Pull the new image
docker-compose pull

# Recreate the containers
docker-compose up -d
```

### Using Specific Version Tags

If you're using specific version tags, update your docker-compose.yml file first:

```yaml
version: '3'
services:
  dockerforge:
    image: dockerforge/dockerforge:2.1.0  # Update this line
    # rest of your configuration...
```

Then apply the changes:

```bash
# Pull the new image
docker-compose pull

# Recreate the containers
docker-compose up -d
```

## Upgrading Production Deployments

For production environments, follow these additional steps:

### 1. Schedule Maintenance Window

Inform users about the planned upgrade and expected downtime.

### 2. Create Complete Backups

Backup all components:

```bash
# Database backup
pg_dump -U dockerforge -d dockerforge > dockerforge_db_backup_$(date +%Y%m%d).sql

# Configuration backup
cp -r /path/to/config /path/to/config.backup-$(date +%Y%m%d)

# Docker volumes backup
docker run --rm -v dockerforge_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/dockerforge-backup-$(date +%Y%m%d).tar.gz /data
```

### 3. Update with Minimal Downtime

#### For Docker Swarm:

```bash
# Update the image in your docker-compose.yml or stack file
# Then update the stack
docker stack deploy -c docker-compose.yml dockerforge
```

#### For Kubernetes:

```bash
# Update the image in your deployment
kubectl set image deployment/dockerforge dockerforge=dockerforge/dockerforge:2.1.0

# Monitor the rollout
kubectl rollout status deployment/dockerforge
```

### 4. Verify Database Migrations

Check logs to ensure database migrations completed successfully:

```bash
# For Docker
docker logs dockerforge | grep -i migration

# For Kubernetes
kubectl logs deployment/dockerforge | grep -i migration
```

### 5. Verify Functionality

After upgrade, verify that all critical functionality is working:

- Container management
- Image operations
- User authentication
- Custom configurations

## Troubleshooting Upgrade Issues

### Database Migration Failures

If you encounter database migration errors:

1. Check the logs for specific error messages:
   ```bash
   docker logs dockerforge
   ```

2. Restore from backup if needed:
   ```bash
   # For PostgreSQL
   psql -U dockerforge -d dockerforge < dockerforge_db_backup_YYYYMMDD.sql
   ```

3. Try manual migration:
   ```bash
   # For Docker installation
   docker exec -it dockerforge dockerforge db upgrade
   ```

### Configuration Compatibility Issues

If your configuration is incompatible with the new version:

1. Check the logs for configuration errors:
   ```bash
   docker logs dockerforge | grep -i config
   ```

2. Update your configuration based on the new version's requirements.

3. If needed, restore the previous configuration and downgrade to the previous version until you can resolve the issues.

### Version Rollback

If you need to rollback to a previous version:

#### For Pip Installation:

```bash
# Uninstall current version
pip uninstall -y dockerforge

# Install specific previous version
pip install dockerforge==1.9.0  # Replace with your previous version

# Restore data from backup if needed
rm -rf ~/.dockerforge
cp -r ~/.dockerforge.backup-YYYYMMDD ~/.dockerforge
```

#### For Docker Installation:

```bash
# Stop current container
docker stop dockerforge
docker rm dockerforge

# Start container with previous version
docker run -d \
  --name dockerforge \
  -p 8080:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v dockerforge_data:/data \
  dockerforge/dockerforge:1.9.0  # Replace with your previous version
```

## Post-Upgrade Tasks

After a successful upgrade:

1. **Clear Browser Cache**: Advise users to clear their browser cache to ensure they get the latest frontend assets.

2. **Update Documentation**: Update your internal documentation to reflect the new version and any changes in functionality.

3. **Review Security Settings**: Check that all security settings are still properly configured after the upgrade.

4. **Performance Testing**: Monitor system performance to ensure the upgrade hasn't negatively impacted performance.

5. **Clean Up Backups**: Once you've verified everything is working correctly, establish a retention policy for your backups.
