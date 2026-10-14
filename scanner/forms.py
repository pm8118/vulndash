from django import forms
from .models import Scan


class ScanForm(forms.ModelForm):
    class Meta:
        model = Scan
        fields = ['target', 'scan_type']
        widgets = {
            'target': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثلاً 192.168.1.1 یا example.com',
            }),
            'scan_type': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        labels = {
            'target': 'هدف اسکن',
            'scan_type': 'نوع اسکن',
        }