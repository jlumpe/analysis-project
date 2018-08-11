"""Provides utilities for managing organized directory of data and analyses."""

from pathlib import Path

import yaml

from .util import PathWrapper, import_by_path, get_frame_ns


DEFAULT_PROJECT_FILENAME = 'project.yaml'


def get_project(path=None, filename=DEFAULT_PROJECT_FILENAME):
	"""Searches through parent directories for the project root.

	Parameters
	----------

	path : str or pathlib.Path
		Directory to search from. Defaults to current working directory.

	filename : str
		Name of file that marks project root and (optionally) contains config.

	Returns
	-------
	.Project

	Raises
	------
	FileNotFoundError
		If the path does not appear to be contained within a project.
	"""
	path = (Path() if path is None else Path(path)).absolute()
	p = path

	while True:
		file = p / filename
		if file.is_file():
			return Project(file)

		if p.parent == p:
			# Reached root of directory tree
			raise FileNotFoundError('{} does not appear to be contained in a project directory'.format(path))

		p = p.parent


class Project:
	"""Represents a directory containing project data, documentation, and analysis code.

	Attributes
	----------

	rootpath : pathlib.Path
		Absolute path to project's root directory.

	config : dict
		JSON-like dictionary containing project configuration.

	rootpathstr : str
		Root path as string.

	rootpathw : analysis_project.util.PathWrapper
		Path wrapper around :attr:`rootpath`, can make locating project files
		from IPython or a Jupyter notebook more convenient.

	Parameters
	----------

	path : str or pathlib.Path
		Path to root directory or config file in root directory.

	config : dict
		Config dictionary. If None will try to load from config file.
	"""

	def __init__(self, path, config=None):
		path = Path(path)

		# Verify root dir and config file
		if path.is_file():
			self.rootpath = path.parent.absolute()
			configfile = path

		elif path.is_dir():
			self.rootpath = path.absolute()

			configfile = path / DEFAULT_PROJECT_FILENAME
			if not configfile.exists():
				configfile = None

		else:
			raise OSError('{} is not a file or directory'.format(path))

		# Get/read config
		if config is not None:
			self.config = config

		elif configfile is not None:
			self.config = self.read_config(configfile)

		# Set attrs from config
		self.name = self.config.get('name')

	@property
	def rootpathstr(self):
		return str(self.rootpath)

	@property
	def rootpathw(self):
		return PathWrapper(self.rootpath)

	@classmethod
	def read_config(cls, file):
		with file.open() as fh:
			return yaml.safe_load(fh)

	def run_ipython(self, pyfile, **kwargs):
		"""Run a Python file and import its contents into the IPython user namespace.

		This should be somewhat equivalent to the ``%run`` magic, which does not
		allow specifying the target file in a dynamic fashion.

		Parameters
		----------

		pyfile : str or pathlib.Path
			Path to Python file to run relative to the project's root directory.

		kwargs: Keyword arguments to
			:meth:`IPython.core.interactiveshell.InteractiveShell.safe_execfile`.
		"""
		from IPython import get_ipython
		shell = get_ipython()

		path = self.rootpath / pyfile

		# Run
		prog_ns = {'__file__': str(path.absolute()), '__name__': '__main__'}
		shell.safe_execfile(str(path), prog_ns, **kwargs)

		# Update user namespace
		for name in ['__file__', '__name__']:
			prog_ns.pop(name, None)
		shell.user_ns.update(prog_ns)

	def import_(self, pyfile, *names, reload=False, magic=False):
		"""Import a script in the project as a module given its path.

		Parameters
		----------
		pyfile : str or pathlib.Path
			Location of python file relative to project root.

		names
			Variable names to import from the module. If given,
			functions like ``from pyfile import name1, name2...``.

		reload : bool
			Reload the module.

		magic : bool
			Instead of returning the module or its attributes, insert them into
			the local namespace of the frame from which the function was called.
			This makes it behave more like the built-in ``import`` statement.

		Returns
		-------
		tuple or types.ModuleType
			Tuple of variables from module if ``names`` is non-empty,
			otherwise the module itself.
			tuple or types.ModuleType
		"""

		path = self.rootpath / pyfile
		if path.suffix != '.py':
			raise ValueError('File must have .py extension')
		if not path.is_file():
			raise FileNotFoundError(pyfile)

		module = import_by_path(path, reload=reload)
		name_values = tuple(getattr(module, name) for name in names)

		if magic:
			globals_, locals_ = get_frame_ns(1)

			if names:
				locals_.update(dict(zip(names, name_values)))
			else:
				locals_[path.stem] = module

			return None

		if names:
			return name_values

		return module
