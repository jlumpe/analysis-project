import os
import types

import pytest

from analysis_project.project import get_project, Project


def test_get_project(test_data_dir):
	pd = test_data_dir / 'test-project-1'

	# Test with root directory and subdirectory as path argument
	paths = [pd, pd / 'scripts']

	for path in paths:
		# Test by passing path as argument
		project = get_project(path)
		assert project.rootpath == pd
		assert project.configfile == pd / 'project.yaml'

		# Test calling with no arguments, should go by working directory
		os.chdir(path)
		project2 = get_project(path)
		assert project2.rootpath == pd
		assert project2.configfile == pd / 'project.yaml'


class test_Project:

	@pytest.fixture()
	def project_dir(self, test_data_dir):
		return test_data_dir / 'test-project-1'

	@pytest.fixture()
	def project(self, project_dir):
		return Project(project_dir)

	def test_construct(self, project_dir):
		config_dict = {'_passed_as_arg': True}

		# Test root directory or config file as path argument
		cases = [
			(project_dir, project_dir / 'project.yaml'),
			(project_dir / 'project.yaml', project_dir / 'project.yaml'),
			(project_dir / 'project2.yaml', project_dir / 'project2.yaml'),
		]

		for path, configfile in cases:
			project = Project(path)
			assert project.rootpath == project_dir
			assert project.configfile == configfile
			assert not project.config.get('_passed_as_arg', False)

			# Try again passing explicit config dict
			project2 = Project(path, config=config_dict)
			assert project2.rootpath == project_dir
			assert project2.configfile is None
			assert project2.config['_passed_as_arg']

	def test_import(self, project):
		rel_path = 'scripts/script.py'

		# Module only
		mod = project._import(rel_path)
		assert isinstance(mod, types.ModuleType)
		assert mod.__file__ == str(project.rootpath / rel_path)
		assert mod.foo == 3

		# Attributes
		foo, bar, baz = project.import_(rel_path, 'foo', 'bar', 'baz')
		assert foo == mod.foo
		assert bar == mod.bar
		assert baz is mod.baz

	def test_import_magic(self, project):
		rel_path = 'scripts/script.py'

		# Module only
		project._import(rel_path, magic=True)
		assert isinstance(script, types.ModuleType)
		assert script.__file__ == str(project.rootpath / rel_path)
		assert script.foo == 3

		# Attributes
		project.import_(rel_path, 'foo', 'bar', 'baz', magic=True)
		assert foo == script.foo
		assert bar == script.bar
		assert baz is script.baz
