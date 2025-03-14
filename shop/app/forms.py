from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,UsernameField, PasswordResetForm,PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import Customer, Address
from django.contrib.auth import views as auth_views

class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'autofocus': 'True',
        'class': 'form-control',
        'placeholder': 'Email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'autocomplete': 'current-password',
        'class': 'form-control',
        'placeholder': 'Mot de passe'
    }))

    def clean_username(self):
        return self.cleaned_data['username'].lower()  
 


class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Old Password', widget = forms.PasswordInput(attrs=
    {'autofocus': 'True', 'autocomplate':'current-password', 'class':'form-control'}))
    new_password1 = forms.CharField(label='New Password', widget = forms.PasswordInput(attrs=
    {'autofocus': 'True', 'autocomplate':'current-password', 'class':'form-control'}))
    new_password2 = forms.CharField(label='Confirm Password', widget = forms.PasswordInput(attrs=
    {'autofocus': 'True', 'autocomplate':'current-password', 'class':'form-control'}))

class MyPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs=
    {'class':'form-control'}))

class MySetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label = 'New Password', widget = forms.PasswordInput(attrs=
    {'autocomplete':'current-password', 'class': 'form-control'}))
    new_password2 = forms.CharField(label = 'Confirm New Password', widget = forms.PasswordInput(attrs=
    {'autocomplete':'current-password', 'class': 'form-control'}))


    
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street_address', 'complement_address', 'city', 'postal_code', 'country']
        widgets = {
            'street_address': forms.TextInput(attrs={'class': 'form-control'}),
            'complement_address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CustomerRegistrationForm(forms.ModelForm):  # On n'hérite plus de UserCreationForm
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # Utiliser l'email comme username
        user.set_password(self.cleaned_data['password'])  # Hacher le mot de passe
        if commit:
            user.save()
            Customer.objects.create(user=user)  # Créer un Customer vide
        return user

class CustomerProfileForm(forms.ModelForm):
    street_address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    complement_address = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    postal_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    country = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    mobile = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Customer
        fields = ['mobile']

    def save(self, user, commit=True):
        customer = user.customer  # Récupérer l'objet Customer lié à l'utilisateur
        customer.mobile = self.cleaned_data['mobile']

        # Vérifie si le customer a déjà une adresse associée
        if customer.address:
            address = customer.address  # Utilise l'adresse existante
        else:
            address = Address()  # Crée une nouvelle adresse

        # Mise à jour des informations d'adresse
        address.street_address = self.cleaned_data['street_address']
        address.complement_address = self.cleaned_data.get('complement_address', '')
        address.city = self.cleaned_data['city']
        address.postal_code = self.cleaned_data['postal_code']
        address.country = self.cleaned_data['country']
        address.save()  # Sauvegarde l'adresse

        # Associer l'adresse au customer et marquer comme complété
        customer.address = address
        customer.is_profile_complete = True  

        if commit:
            customer.save()

        return customer