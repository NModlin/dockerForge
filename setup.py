from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dockerforge",
    version="0.1.0",
    author="DockerForge Team",
    author_email="info@dockerforge.example.com",
    description="A comprehensive Docker management tool with AI-powered troubleshooting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dockerforge/dockerforge",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "dockerforge=src.cli:main",
            "dockerforge-resource-monitor=src.cli_resource_monitoring:main",
            "dockerforge-security=src.cli_security:main",
            "dockerforge-backup=src.cli_backup:main",
            "dockerforge-update=src.cli_update:main",
        ],
    },
    include_package_data=True,
)
