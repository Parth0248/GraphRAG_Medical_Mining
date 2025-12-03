from setuptools import setup, find_packages

setup(
    name="graphrag-medical",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        line.strip() 
        for line in open('requirements.txt').readlines()
        if line.strip() and not line.startswith('#')
    ],
    author="CMPE 255 Team",
    description="GraphRAG for Medical Data Mining",
    python_requires=">=3.8",
)
