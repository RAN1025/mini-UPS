from django import forms
from django.forms import ModelForm
from .models import Package, CustomUser, SearchPackage, Comment

class PackageModelForm(ModelForm):
    class Meta(object):
        model = Package
        fields = '__all__'

        widget = {
            'package_id': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'x': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'y': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'curr_x': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'curr_y': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'status': forms.TextInput(attrs={
                'class': 'form-control',
             }),
            'items': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'amount': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'truck_id': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'owner': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }

class SearchPackageForm(ModelForm):
    class Meta(object):
        model = SearchPackage
        fields = '__all__'

        widget = {
            'package_id': forms.TextInput(attrs={
                'class': 'form-contorl',
                'placeholder': 'Package ID'
            }),
        }

class EditPackageForm(ModelForm):
    class Meta(object):
        model = Package
        fields = ['x','y']

        widget = {
            'x': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'y': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }

class AddCommentForm(ModelForm):
    class Meta(object):
        model = Comment
        fields = '__all__'

        widget = {
            'owner': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'context': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }
