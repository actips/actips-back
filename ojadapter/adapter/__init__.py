from importlib import import_module
import os
import os.path

# for file in os.listdir(os.path.dirname(__file__)):
#     print(file)
#     if not file.startswith('OJAdapter') or not file.endswith('.py'):
#         continue
#     class_name = file.split('.')[0]
#     import_module()

# from .OJAdapterCodeForces import *
# from .OJAdapterHihoCoder import *
from .zoj.adapter import *
