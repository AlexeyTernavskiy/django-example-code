from django import forms
from model_utils import Choices

from src.apps.product.models import ProductModel, CommentModel


class FilterForm(forms.Form):
    FILTER_CHOICE = Choices(
        ('', 'Select one...'),
        ('Like', [('like', 'Like Ascending',), ('-like', 'Like Descending',)]),
        ('Price', [('price', 'Price Ascending',), ('-price', 'Price Descending',)]),
        ('Created', [('created', 'Created Ascending'), ('-created', 'Created Descending',)])
    )

    filter = forms.ChoiceField(
        label='Filter by: ',
        choices=FILTER_CHOICE,
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'c-select'
            })
    )


class ProductForm(forms.ModelForm):
    class Meta:
        model = ProductModel
        exclude = ('user', 'slug',)
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Name',
                    'required': True,
                },
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'cols': 50,
                    'row': 5,
                    'placeholder': 'Description',
                    'required': True,
                },
            ),
            'price': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'number',
                    'step': '0.01',
                    'placeholder': 'Price',
                    'required': True,
                },
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = CommentModel
        fields = ('comment',)
        widgets = {
            'comment': forms.Textarea(
                attrs={
                    'id': 'comment-text',
                    'class': 'form-control',
                    'cols': 50,
                    'row': 3,
                    'placeholder': 'Body of comment',
                    'required': True,
                },
            )
        }
