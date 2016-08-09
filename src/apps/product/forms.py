from django import forms
from model_utils import Choices


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


