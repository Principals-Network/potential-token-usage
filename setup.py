from setuptools import setup, find_packages

setup(
    name="career-planner",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'anthropic',
        'python-dotenv',
    ],
) 