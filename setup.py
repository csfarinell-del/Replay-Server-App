from setuptools import setup, find_packages

# Read the README file for long description
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Virtual Steward Server Configuration Manager"

setup(
    name="replay-server-app",
    version="1.0.0",
    author="AC Server Manager Team",
    author_email="",
    description="A GUI application for managing Assetto Corsa server configurations with Virtual Steward plugin support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/csfarinell-del/Replay-Server-App",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: GNU General Public License v3 (GPLv3)",
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