from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.forms import AuthenticationForm

@login_required
def CerrarSesion(request):
    logout(request)
    return redirect("IniciarSesion")


def IniciarSesion(request):
    if request.method == "GET":
        return render(request, "InicioSesion.html", {"form": AuthenticationForm})
    else:
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"],
        )

        if user is None:
            return render(
                request,
                "login.html",
                {
                    "form": AuthenticationForm,
                    "error": "Usuario o contraseña incorrectos",
                },
            )

        else:
            login(request, user)
            return redirect("InicioTablero")
