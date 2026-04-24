
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

User = get_user_model()

def index(request):
    # El perfil solo se muestra a usuarios autenticados; si no, se redirige al login.
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    else:
        return render(request,'users/profile.html')

def login_view(request):
    # Esta página permite que un usuario existente entre al sistema y acceda a funciones protegidas.
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        # authenticate valida credenciales contra el backend configurado por Django.
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'users/login.html', {'errors':['Invalid Login']})
    else:
        return render(request, 'users/login.html')

def logout_view(request):
    # Cierra la sesión actual y devuelve al usuario al flujo público principal.
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def register_view(request):
    # Esta página crea nuevas cuentas y valida que los datos mínimos sean correctos y seguros.
    if request.method == 'POST':
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        password_confirmation = request.POST.get("password_confirmation", "")
        # Se acumulan errores para devolver toda la retroalimentación en una sola respuesta.
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
                # Se reutilizan las validaciones nativas de Django para exigir una contraseña segura.
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
