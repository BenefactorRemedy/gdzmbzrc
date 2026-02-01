from setuptools import setup, find_packages

setup(
    name="sc-priority-demo-lite",
    version="2.2",
    description="SC-PRIORITY-DEMO-LITE RU v2.2 - Система распределения запасов по приоритетам",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "sc-priority=src.main:main",
        ]
    },
)
