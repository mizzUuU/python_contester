import os
import pathlib

from contester.models import *
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages  # import messages
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes

from .checker import checker
from .forms import *

# Create your views here.


def index(request):
    contests = Contest.objects.all()
    tasks = Task.objects.all()
    return render(request, "HomePage.html", {'contests': contests, 'tasks': tasks})


def auth(request):
    return render(request, "Auth.html")


def test(request):
    return render(request, "bootstrap/test_page.html")


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            print(str(password))
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("index")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="Auth.html", context={"login_form": form})


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("index")


def profile(request):
    return render(request, "profile_page.html")


def rating(request):
    users = Account.objects.all()
    # users = list(users)
    # users.sort(key=lambda x: x.rating, reverse=True)
    return render(request, "rating.html", {'users': users})


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("index")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm
    return render(request=request, template_name="Auth.html", context={"register_form": form})


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = Account.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "password/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'Python Contester',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'admin@example.com', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="password/password_reset.html",
                  context={"password_reset_form": password_reset_form})


def runscript(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            task_id = request.POST.get('task_id', None)
            newdoc = Document(docfile=request.FILES['file'])
            newdoc.save()

            new_path = str(pathlib.Path(newdoc.file.path).parent) + '/' + str(newdoc.id) + \
                       str(pathlib.Path(newdoc.file.path).suffix)
            print(new_path)
            print(newdoc.file.name)

            os.rename(newdoc.file.path, new_path)
            newdoc.file.name = "codes/" + str(newdoc.id) + str(pathlib.Path(newdoc.file.path).suffix)
            newdoc.save()
            result = checker(newdoc.file, task_id)
            res = 0
            for i in result:
                res += i
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            return render(request, 'results.html', {'res': res, 'task_id': id})
    return render(request, 'results.html')


def list(request):
    documents = Document.objects.all()
    return render(request, 'list.html', {'documents': documents})


def getTaskById(request, id):
    task = Task.objects.get(pk=id)
    form = DocumentForm()  # A empty, unbound form
    return render(request, 'task.html', {'task': task, 'form': form, 'task_id': id})


def task_page(request):
    return render(request, "task_page.html")
