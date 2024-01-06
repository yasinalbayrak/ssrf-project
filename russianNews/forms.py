from django import forms

from russianNews.models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)


class ImageUrlForm(forms.Form):
    image_url = forms.URLField(label='Enter the Image URL')