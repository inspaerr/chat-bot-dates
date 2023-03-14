from setuptools import setup, find_packages

setup(
    name="mireabot_dates",
    version="1.0.0",
    description="mirea-datse chat bot",
    author="Sonya Kanchura",
    author_email="oldbox221b@gmail.com",
    packages=find_packages('requirements.txt'),
    entry_points={
        'console_scripts': [
            'mireabot_dates = mireabot_dates.main:run_bot'
        ]
    }
)
