from django import forms
from .models import Paper, Category, Rating

class PaperUploadForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    class Meta:
        model = Paper
        fields = ['title', 'abstract', 'authors', 'publication_date', 'doi', 'pdf_path', 'categories']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'abstract': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'authors': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comma-separated author names'}),
            'publication_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'doi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional DOI'}),
            'pdf_path': forms.FileInput(attrs={'class': 'form-control'}),
        }

class PaperEditForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    class Meta:
        model = Paper
        fields = ['title', 'abstract', 'authors', 'publication_date', 'doi', 'categories']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'abstract': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'authors': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'doi': forms.TextInput(attrs={'class': 'form-control'}),
        }

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)], attrs={'class': 'form-control'}),
            'review_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional review'}),
        }
