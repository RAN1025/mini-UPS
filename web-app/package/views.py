from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.conf import settings

from .models import Package, SearchPackage, Comment
from .forms import SearchPackageForm, PackageModelForm, EditPackageForm, AddCommentForm
# Create your views here.


def indexView(request):
    if not request.user.is_authenticated:
        return redirect('home')
    package = Package.objects.filter(owner=request.user)
    return render(request, 'index.html', {'latest_question_list': package, 'user':request.user})

def editView(request, pk):
    package = get_object_or_404(Package, pk=pk)
    if request.method == 'POST':
        form = EditPackageForm(request.POST, instance=package)
        if form.is_valid():
            package = form.save(commit=False)
            package.save()
            return redirect('package:index')
    else:
        form = EditPackageForm(instance=package)
        return render(request, 'edit.html', {'form': form})

def searchView(request):
    package = None
    if request.method == "POST":
        searchform = SearchPackageForm(request.POST)
        if (searchform.is_valid()):
            post = searchform.save(commit=False)
            post.save()
            package = Package.objects.filter(package_id=post.package_id)
            if package:
                form = PackageModelForm(instance=package[0])
                return render(request, 'search_results.html', {'form': searchform, 'results': package})
            else:
                return render(request, 'search.html', {'latest_question_list': package, 'form':searchform,'message': 'no package found.'})
    else:
        searchform = SearchPackageForm()

    return render(request, 'search.html', {'latest_question_list': package, 'form':searchform})

def commentView(request):
    if not request.user.is_authenticated:
        return redirect('index')
    comment = Comment.objects.all()
    return render(request, 'comment.html', {'latest_question_list': comment, 'user':request.user})

def addcommentView(request):
    if request.method == "POST":
        form = AddCommentForm(request.POST)
        if form.is_valid():
            owner = form.cleaned_data['owner']
            context = form.cleaned_data['context']
            comment = Comment.objects.create(owner=owner,context=context)
            comment.save()
            return redirect('package:comment')
    else:
        form = AddCommentForm()
        return render(request,'addcomment.html',{'form':form})
