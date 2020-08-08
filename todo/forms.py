from django.forms import ModelForm
from .models import Todo


# ModelFrom - used for creation of forms from models
class TodoForm(ModelForm):
    # Specify the form's fields inside the inner Meta class
    class Meta:
        model = Todo
        fields = ['title', 'description', 'important']
