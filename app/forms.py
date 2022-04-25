from django import forms
from .models import Bid
class BidForms(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['time','bidPrice']

