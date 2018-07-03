from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.core.mail import EmailMessage
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_list_or_404, get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _
from .forms import SignupForm, UserForm, PasswordChangeForm, TodoListForm, PostEditForm
from .tokens import account_activation_token
from .models import User, TodoList
from django.views.generic import CreateView, ListView, UpdateView
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger


def signup(request):
    if request.user.is_authenticated():
        return redirect('view_profile')
    else:
        if request.method == 'POST':
            form = SignupForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                subject = 'Activate your accounts.'
                message = render_to_string('accounts/activation_email.html', {
                    'user':user, 'domain':current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                toemail = form.cleaned_data.get('email')
                email = EmailMessage(subject, message, to=[toemail])
                email.send()
                return render(request, 'accounts/activation_pending.html')
        else:
            form = SignupForm()
        return render(request, 'registration/register.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.backend='django.contrib.auth.backends.ModelBackend'
        user.save()
        login(request, user)
        return render(request, 'accounts/activation_completed.html')
    else:
        return HttpResponse('Activation link is invalid!')

def index(request):
    if request.user.is_authenticated:
        return redirect('userpage')
    else:
        return redirect('login')

@login_required
def userpage(request):
    username = None
    if request.user.country:
       return redirect('list')
    else:
       return redirect('update_profile')

@method_decorator(login_required, name='dispatch')
class TodoListView(ListView):
    model = TodoList
    paginate_by = 5
    context_object_name = 'todo_posts'
    template_name = 'accounts/mylist.html'

    def get_queryset(self):
        user_id = self.request.user.id
        queryset = TodoList.objects.filter(owner_id=user_id) \
            .order_by('-created')
        return queryset

    def get_context_data(self, **kwargs):
        user_id = self.request.user.id
        context = super(TodoListView, self).get_context_data(**kwargs) 
        list_todo = TodoList.objects.filter(owner_id=user_id)
        paginator = Paginator(list_todo, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            file_todo = paginator.page(page)
        except PageNotAnInteger:
            file_todo = paginator.page(1)
        except EmptyPage:
            file_todo = paginator.page(paginator.num_pages)
        context['list_todo'] = TodoList
        return context

@method_decorator(login_required, name='dispatch')
class FeedListView(ListView):
    model = TodoList
    paginate_by = 5
    context_object_name = 'todo_posts'
    template_name = 'accounts/list.html'

    def get_queryset(self):
        user_id = self.request.user.id
        queryset = TodoList.objects.all() \
            .order_by('-created')
        return queryset

    def get_context_data(self, **kwargs):
        user_id = self.request.user.id
        context = super(FeedListView, self).get_context_data(**kwargs) 
        list_todo = TodoList.objects.all()
        paginator = Paginator(list_todo, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            file_todo = paginator.page(page)
        except PageNotAnInteger:
            file_todo = paginator.page(1)
        except EmptyPage:
            file_todo = paginator.page(paginator.num_pages)
        context['list_todo'] = TodoList
        return context

@login_required
def edit_post(request,id):
    user_id = request.user.id
    post = TodoList.objects.get(id=id)
    if request.method == 'POST':
        edit_form = PostEditForm(request.POST, instance=post)
        if edit_form.is_valid():
                edit = edit_form.save(commit=False)
                user = User.objects.get(id=user_id)
                edit.owner = user
                edit.save()
                edit_form.save()
                return redirect('mylist')
    else:
        edit_form = PostEditForm(instance=post)
    return render(request, 'accounts/edit_post.html', {
        'edit_form':edit_form,
        })

@login_required
def delete_post(request,id):
    user_id = request.user.id
    post = TodoList.objects.get(id=id)
    post.delete()
    return redirect('mylist')

@login_required
def view_profile(request):
    user_id = request.user.id
    if request.method == 'POST':
        todo_form = TodoListForm(request.POST)
        if todo_form.is_valid():
            todo = todo_form.save(commit=False)
            user = User.objects.get(id=user_id)
            todo.owner = user
            todo.save()
            todo_form.save()
            messages.success(request, _('Your profile was successfully updated!'))
            return redirect('view_profile')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        todo_form = TodoListForm(request.POST)
        todo_posts = TodoList.objects.filter(owner_id=user_id).order_by('created')
    return render(request, 'accounts/view_profile.html', {
        'todo_form':todo_form,
        })

@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST' and 'profile' in request.POST:
        user_form = UserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, _('Your profile was successfully updated!'))
            return redirect('view_profile')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {
        'user_form': user_form,
    })

@login_required
@transaction.atomic
def change_password(request):
    if request.user.has_usable_password():
        PasswordForm = PasswordChangeForm
    else:
        PasswordForm = AdminPasswordChangeForm
    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('view_profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordForm(request.user)
    return render(request, 'registration/password.html', {
        'form': form
    })

