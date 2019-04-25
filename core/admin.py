from django.contrib import admin

from django.db import models

from . import models as m

for k, model in m.__dict__.items():
    # if issubclass(models.Model, type(model)):
    try:
        admin.site.register(model)
        print(k, model)
    except:
        pass
