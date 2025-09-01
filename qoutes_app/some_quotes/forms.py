from django.db.models import Count
from django.forms import ModelForm, TextInput, Select, Textarea, NumberInput
from .models import Quote, Source

class SourceForm(ModelForm):
    class Meta:
        model = Source
        fields = ['title']
        widgets = {
            'title':    TextInput(attrs={'class': 'form-control', 'placeholder': 'Название источника'}),
        }

class QuoteForm(ModelForm):
    class Meta:
        model = Quote
        fields = ['text', 'source', 'weight']
        widgets = {
            'text': Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'source': Select(attrs={'class': 'form-control'}),
            'weight': NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['source'].queryset = Source.objects.annotate(
            quote_count=Count('quotes')
        ).filter(quote_count__lt=3).order_by('title')
