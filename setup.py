from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Async data ingestion pipeline with retry, circuit breaker, and job tracking"

setup(
    name="async-data-ingestion-pipeline",
    version="2.0.0",
    author="MERCURY-OPS",
    description="Async data ingestion pipeline with retry, circuit breaker, and job tracking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mercury-systems/async-data-ingestion-pipeline",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.111.0",
        "uvicorn>=0.30.1",
        "httpx>=0.27.0",
        "pydantic>=2.7.4",
        "pydantic-settings>=2.3.4",
    ],
    extras_require={
        "dev": ["pytest>=8.2.2", "pytest-asyncio>=0.23.7", "httpx>=0.27.0"],
    },
)
