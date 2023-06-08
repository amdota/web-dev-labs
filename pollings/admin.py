from django.contrib import admin

from pollings.models import Question, Answer

admin.site.register(Question)
admin.site.register(Answer)
