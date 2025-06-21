from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="textfission",
    version="0.1.0",
    author="Sun Zhihan",
    author_email="sunzhihan20@mails.ucas.edu.cn",
    description="A powerful Python library for intelligent text processing, question generation, and answer generation for LLM fine-tuning datasets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GeoSzh/text-fission",
    project_urls={
        "Bug Reports": "https://github.com/GeoSzh/text-fission/issues",
        "Source": "https://github.com/GeoSzh/text-fission",
        "Documentation": "https://github.com/GeoSzh/text-fission#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "all": [
            "openai>=1.0.0",
            "langchain>=0.0.200",
            "dashscope>=1.0.0",
            "erniebot>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "textfission=textfission.cli:main",
        ],
    },
    keywords="nlp, text-processing, question-generation, llm, fine-tuning, dataset, ai, machine-learning",
    include_package_data=True,
    zip_safe=False,
) 