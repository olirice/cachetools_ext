from setuptools import setup, find_packages


DEV_REQUIRES = ["pytest", "pytest-cov", "pre-commit", "pylint", "black", "mypy"]

setup(
    name = "cachetools_ext",
    version = "0.0.1",
    packages = find_packages(exclude=("test")),
    install_requires=[],
    extras_require= {"dev": DEV_REQUIRES}
)
