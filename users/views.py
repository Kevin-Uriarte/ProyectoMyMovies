
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

User = get_user_model()

def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    else:
        return render(request,'users/profile.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return HttpResponseRedirect(reverse('index'))
        else:
            # Return an 'invalid login' error message.
            return render(request, 'users/login.html', {'errors':['Invalid Login']})
    else:
        return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        password_confirmation = request.POST.get("password_confirmation", "")
        errors = []

        if not username:
            errors.append("El nombre de usuario es obligatorio.")

        if not password:
            errors.append("La contraseña es obligatoria.")

        if password != password_confirmation:
            errors.append("Las contraseñas no coinciden.")

        if User.objects.filter(username=username).exists():
            errors.append("Ese nombre de usuario ya está registrado.")

        if not errors:
            try:
                validate_password(password, user=User(username=username))
            except ValidationError as exc:
                errors.extend(exc.messages)

        if errors:
            return render(
                request,
                'users/register.html',
                {
                    'errors': errors,
                    'values': {
                        'username': username,
                    }
                }
            )

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return HttpResponseRedirect(reverse('index'))

    return render(request, 'users/register.html')
