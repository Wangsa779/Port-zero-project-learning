 from setuptools import setup, find_packages

setup(
    name="portzero",
    version="0.1.0",
    author="Wangsa",
    description="Enhanced Multi-threaded Port Scanner with nmap-like features",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Wangsa779/Port-zero-project-learning.git",  # update with your repo URL
    packages=find_packages(),
    install_requires=[
        "pyfiglet",
        "scapy"
    ],
    entry_points={
        "console_scripts": [
            "Port-zero-project-learning=portzero.scanner:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Security",
    ],
    python_requires=">=3.7",
)
