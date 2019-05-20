from django.shortcuts import render, redirect, render_to_response
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect

from .forms import CustomUserCreationForm, CustomUserChangeForm

# Create your views here.
class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect(reverse('package:index'))

    else:
        form = CustomUserChangeForm(instance=request.user)
        args = {'form': form}
        return render(request, 'profile.html', args)
