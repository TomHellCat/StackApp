from django import forms

class SearchForm(forms.Form):
    tag = forms.CharField(label='tag', max_length=100)
    title = forms.CharField(label='title', max_length=100)