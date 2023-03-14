from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="mireabot_dates",
    version="1.0.0",
    description="mirea-dates chat bot",
    author="Sonya Kanchura",
    author_email="oldbox221b@gmail.com",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'mireabot_dates = mireabot_dates.telegram:run_bot'
        ]
    },
    install_requires=required
)
