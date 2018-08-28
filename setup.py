from setuptools import setup, find_packages
from os import path


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
	name     = 'sumtype',
	version  = '0.9.0',
	packages = find_packages(exclude=['tests']),
	install_requires = ['indented'],

	description      = 'Create sum types easily',
	long_description = long_description,
	long_description_content_type = "text/markdown",
	keywords = 'sum variant tagged union enum type types',

	author       = 'J Uryga',
	author_email = 'lolzatu2@gmail.com',
	project_urls = {
		'Source': 'https://github.com/lubieowoce/sumtype',
	},
)

