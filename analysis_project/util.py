"""Misc utility functions and classes."""

from pathlib import Path
import re


def import_by_path(path, reload=False):
	"""Import a module given a path to the source file.

	Parameters
	----------

	path : str or pathlib.Path
		Path to module file.

	reload : bool
		Reload the module before returning it.

	Returns
	-------
	types.ModuleType
		The imported module.
	"""
	import sys
	from importlib import __import__, reload as rld

	# Prepend file's directory to import path
	path = Path(path)
	sys.path.insert(0, str(path.parent))

	try:
		module = __import__(path.stem)
		if reload:
			rld(module)
		return module

	finally:
		# Restore sys.path
		del sys.path[0]


def get_frame_ns(up=0):
	"""Get the global and local namespaces from a parent stack frame.

	Parameters
	----------

	up : int
		Number of stack frames to move up. 0 corresponds to the frame calling
		the function.

	Returns
	-------
	tuple[dict]
		``(globals, locals)``
	"""
	from inspect import currentframe

	frame = currentframe()
	try:

		# Move up the stack
		for _ in range(up + 1):
			frame = frame.f_back

		return frame.f_globals, frame.f_locals

	finally:
		# Prevents reference cycle, see documentation for inspect module
		del frame


class PathWrapper:
	"""
	Wrapper around a file path object that supports accessing directory children
	by attribute access and ``__getitem__`` syntax, enabling tab completion in
	IPython.

	To be used with :class:`.Project` for convenience when specifying paths
	relative to the project root.

	Directory children are accessible as attributes. Attribute names are the
	file/directory names with runs of invalid characters collapsed to
	underscores. The string ``'d__'`` is prependend to names that begin with a
	digit. If there are conflicts, files with the exact same name as the
	attribute are favored, followed by alphabetical ordering.

	Also implements the dunder methods of the mapping interface, but not the
	regular named methods (``keys()``, ``values()``, etc.).

	Attributes
	----------

	_p : pathib.Path

		The wrapped file path object.
	"""
	def __init__(self, path):
		self.__path = Path(path)

	@property
	def _p(self):
		return self.__path

	def __len__(self):
		return len(list(self.__path.iterdir()))

	def __iter__(self):
		return (f.name for f in self.__path.iterdir())

	def __contains__(self, name):
		return (self.__path / name).exists()

	def __getitem__(self, name):
		return PathWrapper(self.__path / name)

	def __getattr__(self, name):
		p = self.__path / name
		if p.exists():
			return PathWrapper(p)

		for p in sorted(self.__path.iterdir()):
			if name == self._file_to_attr(p.name):
				return PathWrapper(p)

		raise AttributeError(name)

	@classmethod
	def _file_to_attr(self, name):
		if re.fullmatch(r'[_a-zA-Z0-9]\w*', name):
			return name

		attr = re.sub('\W+', '_', name)
		attr = re.sub(r'^(\d)', r'd__\1', attr)

		return attr

	def __dir__(self):
		return [
			*type(self).__dict__,
			*self.__dict__,
			*map(self._file_to_attr, self),
		]

	def __str__(self):
		return str(self.__path)

	def __fspath__(self):
		return str(self.__path)

	def _ipython_key_completions_(self):
		return sorted(self)

	def __repr__(self):
		return '%s(%r)' % (type(self).__name__, str(self.__path))
