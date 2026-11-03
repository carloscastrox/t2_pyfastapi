from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=50, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=50, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'})
    )
    full_name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre Completo'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

class ProductForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    price = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    stock = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    category = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    image_url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))