from setuptools import setup, find_packages

setup(
    name="AWScanner",
    version="2",
    packages=find_packages(),
    description="AWS IP range scanner with Masscan and TLS analysis",
    author="q1ncite",
    author_email="q1ncite@proton.me",
    url="https://github.com/sherlockteen/AWScanner",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "AWScanner=AWScanner.main:main",
        ],
    },
    python_requires='>=3.6',
)
