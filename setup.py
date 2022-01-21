from setuptools import setup, find_packages

setup(
    name='gh_scrape',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'BeautifulSoup4',
        'Requests',
        'Pandas'
    ],
    entry_points={
        'console_scripts': [
            'ghs=src.gh_scrape:ghs',
        ],
    }
)
