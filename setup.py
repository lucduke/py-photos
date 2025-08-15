#!/usr/bin/env python3
"""
Setup script for py-photos package
"""

from setuptools import setup, find_packages

setup(
    name="py-photos",
    version="1.0.0",
    description="A package for car number recognition in photos",
    author="Assistant Claude",
    author_email="assistant.claude@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "anthropic",
        "python-dotenv",
        "pillow",
        "rawpy",
        "imageio"
    ],
    entry_points={
        "console_scripts": [
            "py-photos=main:main"
        ]
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)