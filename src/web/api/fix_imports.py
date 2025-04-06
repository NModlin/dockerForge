"""
Fix imports script for DockerForge Web UI API.

This script fixes relative imports to absolute imports in all router files.
"""

import os
import re


def fix_router_imports(file_path):
    """
    Fix relative imports in a router file.
    """
    with open(file_path, "r") as f:
        content = f.read()

    # Replace relative imports with absolute imports
    content = re.sub(r"from \.\.(.*?) import", r"from \1 import", content)
    content = re.sub(r"from \.\.(.*)", r"from \1", content)

    with open(file_path, "w") as f:
        f.write(content)

    print(f"Fixed imports in {file_path}")


def main():
    """
    Fix imports in all router files.
    """
    router_dir = os.path.dirname(os.path.abspath(__file__)) + "/routers"
    for filename in os.listdir(router_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            file_path = os.path.join(router_dir, filename)
            fix_router_imports(file_path)

    print("All router imports fixed successfully!")


if __name__ == "__main__":
    main()
