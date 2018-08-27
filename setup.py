from setuptools import setup, find_packages

setup(
	name = 'sumtype',
	description = 'Create sum types easily',
	version  = '0.9.0',
	packages = find_packages(exclude=['tests']),

	keywords = 'sum variant tagged union type types',
)