# DockerForge Version Management

This document outlines the version management strategy for DockerForge, including versioning scheme, release process, and version compatibility considerations.

## Versioning Scheme

DockerForge follows [Semantic Versioning (SemVer)](https://semver.org/) with the format `MAJOR.MINOR.PATCH`:

- **MAJOR**: Incremented for incompatible API changes or significant architectural changes
- **MINOR**: Incremented for new functionality added in a backward-compatible manner
- **PATCH**: Incremented for backward-compatible bug fixes

Additional labels for pre-release and build metadata are available as extensions to the MAJOR.MINOR.PATCH format:

- **Pre-release**: Appended with a hyphen (e.g., `1.2.3-alpha.1`, `1.2.3-beta.2`)
- **Build metadata**: Appended with a plus sign (e.g., `1.2.3+20230501`, `1.2.3-beta.1+exp.sha.5114f85`)

## Release Channels

DockerForge provides multiple release channels to accommodate different user needs:

### Stable Releases

- Thoroughly tested and recommended for production use
- Available as:
  - PyPI package: `pip install dockerforge`
  - Docker image: `dockerforge/dockerforge:latest` or `dockerforge/dockerforge:1.2.3`

### Development Releases

- Latest features but may contain bugs
- Available as:
  - PyPI package: `pip install --pre dockerforge`
  - Docker image: `dockerforge/dockerforge:develop`

### Nightly Builds

- Built from the latest code, may be unstable
- Available as:
  - Docker image: `dockerforge/dockerforge:nightly`

## Release Cycle

DockerForge follows a regular release cycle:

- **PATCH releases**: Approximately every 2-4 weeks for bug fixes
- **MINOR releases**: Approximately every 2-3 months for new features
- **MAJOR releases**: As needed for significant changes, typically once a year

### Release Process

1. **Planning Phase**:
   - Features and bug fixes are planned for the upcoming release
   - Issues are assigned to milestones in the issue tracker

2. **Development Phase**:
   - Features are developed in feature branches
   - Pull requests are reviewed and merged into the `develop` branch

3. **Testing Phase**:
   - Automated tests run on the `develop` branch
   - Beta releases are created for user testing
   - Feedback is collected and issues are addressed

4. **Release Phase**:
   - Release branch is created from `develop`
   - Final testing and bug fixes are applied
   - Version numbers are updated
   - Release is tagged and published
   - Release notes are published

## Version Compatibility

### API Compatibility

- **MAJOR version changes**: May include breaking API changes
- **MINOR and PATCH version changes**: Maintain backward compatibility for public APIs

### Database Compatibility

- Database schema migrations are included with each release
- Downgrading to a previous version may require a database rollback

### Configuration Compatibility

- Configuration file format changes are documented in release notes
- MAJOR version changes may require configuration updates

## Long-Term Support (LTS)

Selected releases are designated as Long-Term Support (LTS) versions:

- LTS releases receive security updates and critical bug fixes for at least 12 months
- LTS releases are recommended for enterprise environments
- Current LTS version: 1.0.x (supported until 2024-06-30)

## Version Management Tools

DockerForge provides tools to help manage versions:

### Version Check Command

```bash
dockerforge version --check
```

This command:
- Displays the current installed version
- Checks for available updates
- Indicates if the current version is supported

### Version History Command

```bash
dockerforge version --history
```

This command displays the release history with dates and key changes.

## Upgrading Between Versions

Guidelines for upgrading between different version types:

### PATCH Version Upgrades

- Generally safe to apply immediately
- Minimal risk of issues
- Example: 1.2.3 to 1.2.4

### MINOR Version Upgrades

- Review release notes before upgrading
- Test in non-production environment if possible
- Example: 1.2.3 to 1.3.0

### MAJOR Version Upgrades

- Carefully review release notes and upgrade guide
- Test thoroughly in non-production environment
- Plan for potential configuration changes
- Example: 1.2.3 to 2.0.0

## Version Pinning

In production environments, it's recommended to pin to specific versions:

### In pip requirements:

```
dockerforge==1.2.3
```

### In Docker Compose:

```yaml
services:
  dockerforge:
    image: dockerforge/dockerforge:1.2.3
```

## Release Notes

Release notes for all versions are available at:

- [GitHub Releases](https://github.com/NModlin/dockerForge/releases)
- [Documentation Website](https://docs.dockerforge.io/releases/)

Release notes include:
- New features
- Bug fixes
- Breaking changes
- Deprecation notices
- Upgrade instructions

## Version Support Policy

- **Active Support**: Latest MAJOR.MINOR release receives bug fixes and security updates
- **Maintenance Support**: Previous MINOR releases receive security updates only
- **End of Life**: Versions older than 12 months or two MAJOR releases no longer receive updates

## Checking Current Version

You can check your current DockerForge version in several ways:

### Command Line

```bash
dockerforge --version
```

### Web Interface

1. Log in to DockerForge
2. Go to Settings > About
3. Version information is displayed at the top of the page

### API

```bash
curl http://localhost:8080/api/v1/version
```

Response:
```json
{
  "version": "1.2.3",
  "build_date": "2023-05-01",
  "git_commit": "a1b2c3d",
  "api_version": "1"
}
```
