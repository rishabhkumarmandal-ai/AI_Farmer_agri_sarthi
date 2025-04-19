from django import forms
from .models import Community

class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['box']
        labels = {
            'box': 'Community Description',  
        }
        widgets = {
            'box': forms.Textarea(attrs={
                'placeholder': 'Enter community description here...',
                'rows': 4,  # Specify the number of visible rows
                'class': 'form-control' 
            }),
        }

    def clean_box(self):
        data = self.cleaned_data['box']
        if len(data) < 10:
            raise forms.ValidationError("Description must be at least 10 characters long.")
        return data

