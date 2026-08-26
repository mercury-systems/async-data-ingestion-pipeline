from setuptools import setup, find_packages

setup(
    name="async-data-ingestion-pipeline",
    version="1.0.0",
    author="MERCURY-OPS",
    author_email="ops@mercury-systems.dev",
    description="High-throughput async data ingestion pipeline with FastAPI",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    url="https://github.com/mercury-systems/async-data-ingestion-pipeline",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    install_requires=[
        "fastapi>=0.111.0",
        "uvicorn>=0.30.1",
        "httpx>=0.27.0",
        "pydantic>=2.7.4",
        "pydantic-settings>=2.3.4",
    ],
    extras_require={
        "dev": ["pytest>=8.2.2", "pytest-asyncio>=0.23.7"],
    },
)
