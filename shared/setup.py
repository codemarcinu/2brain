from setuptools import setup, find_packages

setup(
    name="obsidian-brain-shared",
    version="2.0.0",
    description="Shared library for Obsidian Brain microservices",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "redis>=5.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "python-dotenv>=1.0.0",
        "structlog>=24.0.0",
    ],
    python_requires=">=3.10",
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
        ]
    },
)
