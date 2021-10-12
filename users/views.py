# coding=utf-8
from django.views.generic import CreateView

from users.forms import CreationForm


class SignUpView(CreateView):
    form_class = CreationForm
    success_url = '/auth/login/'
    template_name = 'signup.html'
