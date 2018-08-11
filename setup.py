"""Setuptools installation script for analysis-project package."""

from setuptools import setup


# Get contents of README file
with open('README.md') as fh:
	readme_contents = fh.read()


requirements = [
]

setup_requirements = ['pytest-runner']

test_requirements = ['pytest']


setup(
	name='analysis-project',
	version='0.1',
	description='Python package for managing scripts and data for a scientific data analysis or data science project.',
	long_description=readme_contents,
	author='Jared Lumpe',
	author_email='mjlumpe@gmail.com',
	url='https://github.com/jlumpe/analysis-project',
	python_requires='>=3.5',
	install_requires=requirements,
	setup_requires=setup_requirements,
	test_requires=test_requirements,
	include_package_data=True,
	license='MIT',
	# classifiers='',
	# keywords=[],
	# platforms=[],
	# provides=[],
	# requires=[],
	# obsoletes=[],
)
