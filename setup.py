import sys
from setuptools import setup, find_packages

# Read the README file for long description
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Assetto Corsa Server Configuration Manager"

setup(
    name="assetto-corsa-server-manager",
    version="1.0.0",
    author="AC Server Manager Team",
    author_email="",
    description="A GUI application for managing Assetto Corsa server configurations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/assetto-corsa-server-manager",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
    ],
    python_requires=">=3.6",
    install_requires=[
        "PyQt5>=5.12",
    ],
    entry_points={
        "console_scripts": [
            "ac-server-manager=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)