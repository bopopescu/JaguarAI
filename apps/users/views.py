from django.views.generic import FormView

from django import forms

from apps.users.models import JaguarUser


class ResetPasswordForm(forms.Form):
    code = forms.CharField(label='Reset Code')
    password1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_code(self):
        try:
            code = self.cleaned_data.get("code")
            JaguarUser.objects.get(password_reset_key=code)
        except JaguarUser.DoesNotExist:
            raise forms.ValidationError("Invalid code")


class PasswordResetView(FormView):
    template_name = 'reset.html'
    form_class = ResetPasswordForm
    success_url = '/'

    def form_valid(self, form: forms.Form):
        form.clean()
        code = form.data.get("code")
        password = form.cleaned_data.get("password2")
        user = JaguarUser.objects.get(password_reset_key=code)
        user.set_password(password)
        user.save()
        return super().form_valid(form)
