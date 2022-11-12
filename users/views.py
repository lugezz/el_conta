from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.contrib.auth.decorators import login_required

from .forms import RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm


class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    def dispatch(self, request, *args, **kwargs):
        # Será redirigido a la página de inicio si ya está logueado
        if request.user.is_authenticated:
            return redirect(to='/')

        # en caso contrario sigue el curso normal
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Cuenta creada como {username}')

            return redirect(to='login')

        return render(request, self.template_name, {'form': form})


class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # para que la sesión expire a los 0 segundos
            self.request.session.set_expiry(0)

            # fuerza el registro en las cookies
            self.request.session.modified = True

        # Caso contrario la sesión durara lo que la session cookie time sea "SESSION_COOKIE_AGE" definido en settings.py
        return super(CustomLoginView, self).form_valid(form)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject'
    success_message = "Le hemos enviado instrucciones por correo electrónico " \
                      "para establecer su contraseña, si existe una cuenta con "\
                      "el correo electrónico que ingresó. Deberías recibirlos en "\
                      "breve. \n" \
                      "Si no recibe un correo electrónico, asegúrese de haber "\
                      "ingresado la dirección con la que se registró y verifique "\
                      "su carpeta de correo no deseado."
    success_url = reverse_lazy('homepage')


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = "Contraseña modificada correctamente"
    success_url = reverse_lazy('users-home')


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Su perfil ha sido actualizado correctamente')
            return redirect(to='users-profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})
