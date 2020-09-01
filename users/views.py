from django.views.generic import CreateView

from .forms import CreationForm


class SignUpView(CreateView):
    form_class = CreationForm
    success_url = '/auth/login/'
    template_name = 'signup.html'
