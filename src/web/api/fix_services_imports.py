"""
Fix imports script for DockerForge Web UI API services.

This script fixes relative imports to absolute imports in all service files.
"""

import os
import re


def fix_service_imports(file_path):
    """
    Fix relative imports in a service file.
    """
    with open(file_path, "r") as f:
        content = f.read()

    # Replace relative imports with absolute imports
    content = re.sub(r"from \.\.(.*?) import", r"from \1 import", content)
    content = re.sub(r"from \.\.(.*)", r"from \1", content)
    content = re.sub(r"from \.(.*?) import", r"from services.\1 import", content)
    content = re.sub(r"from \.(.*)", r"from services.\1", content)

    with open(file_path, "w") as f:
        f.write(content)

    print(f"Fixed imports in {file_path}")


def main():
    """
    Fix imports in all service files.
    """
    service_dir = os.path.dirname(os.path.abspath(__file__)) + "/services"
    if os.path.exists(service_dir):
        for filename in os.listdir(service_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                file_path = os.path.join(service_dir, filename)
                fix_service_imports(file_path)

        print("All service imports fixed successfully!")
    else:
        print(f"Service directory not found: {service_dir}")


if __name__ == "__main__":
    main()
