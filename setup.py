from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="game2048",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Implementacja gry 2048 w Pythonie z dodatkowymi funkcjami",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/2048",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment :: Puzzle Games",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: Polish",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        'dev': [
            'black>=23.3.0',
            'flake8>=6.0.0',
            'mypy>=1.3.0',
            'pytest>=7.3.1',
            'pytest-cov>=4.0.0',
            'sphinx>=7.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'game2048=main2048.__main__:main',
        ],
    },
) 