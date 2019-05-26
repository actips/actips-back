import os.path
import inspect

from importlib import import_module
from .OJAdapterBase import OJAdapterBase

ALL_ADAPTERS = dict()

for file in os.listdir(os.path.dirname(__file__)):
    file_path = os.path.join(os.path.dirname(__file__), file, 'adapter.py')
    if os.path.isfile(file_path):
        mod = import_module('ojadapter.adapter.' + file + '.adapter')
        for k in dir(mod):
            cls = getattr(mod, k)
            if inspect.isclass(cls) and issubclass(cls, OJAdapterBase) \
                    and cls != OJAdapterBase and cls.code:
                ALL_ADAPTERS[cls.code] = cls()
