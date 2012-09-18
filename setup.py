from distutils.core import setup

setup(
    name='ubu_scraper',
    version='0.1',
    author='Jacob M. Johnson',
    author_email='jake@archive.org',
    packages=['ubu'],
    scripts=['bin/ubu_get'],
    url='https://github.com/jjjake/ubu',
    description='A simple python library for scraping ubu.com',
    long_description=open('README.md').read(),
)
