from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from core.models import User
from .forms import RegistrationForm, LoginForm

def home_redirect(request):
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role'] or 'user'

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role=role
            )
            # Create a mentor profile if the user registered as a mentor
            if role == 'mentor':
                from core.models import Mentor
                Mentor.objects.get_or_create(
                    user=user,
                    defaults={
                        'title': 'Professional Mentor',
                        'company': 'Independent',
                        'bio': 'Mentor on SheShield AI platform.',
                    }
                )

            login(request, user)
            messages.success(request, f'Welcome to SheShield AI, {first_name}! 🎉')
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = RegistrationForm()
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is None:
                try:
                    u = User.objects.get(email=email)
                    user = authenticate(request, username=u.username, password=password)
                except User.DoesNotExist:
                    user = None
            if user:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')


def forgot_password_view(request):
    if request.method == 'POST':
        messages.success(request, 'Password reset link has been sent to your email.')
        return redirect('login')
    return render(request, 'auth/forgot_password.html')


def reset_password_view(request):
    return render(request, 'auth/forgot_password.html')


import os
from django.conf import settings

def load_gemini_key():
    env_path = os.path.join(settings.BASE_DIR, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    k, v = line.strip().split('=', 1)
                    if k.strip() == 'GEMINI_API_KEY':
                        return v.strip().strip("'").strip('"')
    return ""

def save_gemini_key(key):
    env_path = os.path.join(settings.BASE_DIR, '.env')
    lines = []
    found = False
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('GEMINI_API_KEY='):
                    lines.append(f"GEMINI_API_KEY={key}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"GEMINI_API_KEY={key}\n")
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def load_twilio_settings():
    env_path = os.path.join(settings.BASE_DIR, '.env')
    config = {
        'TWILIO_ACCOUNT_SID': '',
        'TWILIO_AUTH_TOKEN': '',
        'TWILIO_PHONE_NUMBER': ''
    }
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    k, v = line.strip().split('=', 1)
                    k_str = k.strip()
                    if k_str in config:
                        config[k_str] = v.strip().strip("'").strip('"')
    return config

def save_twilio_settings(sid, token, phone):
    env_path = os.path.join(settings.BASE_DIR, '.env')
    lines = []
    keys_to_update = {
        'TWILIO_ACCOUNT_SID': sid,
        'TWILIO_AUTH_TOKEN': token,
        'TWILIO_PHONE_NUMBER': phone
    }
    updated = set()
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line:
                    line_key = line.split('=', 1)[0].strip()
                    if line_key in keys_to_update:
                        lines.append(f"{line_key}={keys_to_update[line_key]}\n")
                        updated.add(line_key)
                        continue
                lines.append(line)
    for k, v in keys_to_update.items():
        if k not in updated:
            lines.append(f"{k}={v}\n")
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

@login_required
def settings_view(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'language':
            lang = request.POST.get('language')
            tz = request.POST.get('timezone')
            request.session['django_language'] = lang
            request.session['timezone'] = tz
            messages.success(request, f'Language & Region settings saved successfully!')
        elif form_type == 'notifications':
            messages.success(request, 'Notification preferences updated successfully!')
        elif form_type == 'privacy':
            is_sharing = request.POST.get('location_sharing') == 'on'
            request.user.is_location_sharing = is_sharing
            request.user.save(update_fields=['is_location_sharing'])
            messages.success(request, 'Privacy & Security settings updated successfully!')
        elif form_type == 'ai_coach':
            key = request.POST.get('gemini_api_key', '').strip()
            save_gemini_key(key)
            os.environ['GEMINI_API_KEY'] = key
            messages.success(request, 'Gemini API Key updated successfully!')
        elif form_type == 'twilio_sms':
            sid = request.POST.get('twilio_account_sid', '').strip()
            token = request.POST.get('twilio_auth_token', '').strip()
            phone = request.POST.get('twilio_phone_number', '').strip()
            save_twilio_settings(sid, token, phone)
            os.environ['TWILIO_ACCOUNT_SID'] = sid
            os.environ['TWILIO_AUTH_TOKEN'] = token
            os.environ['TWILIO_PHONE_NUMBER'] = phone
            messages.success(request, 'Twilio SMS settings updated successfully!')
        else:
            messages.success(request, 'Settings updated successfully!')
        return redirect('settings')
    
    gemini_api_key = load_gemini_key()
    twilio_config = load_twilio_settings()
    return render(request, 'settings/settings.html', {
        'gemini_api_key': gemini_api_key,
        'twilio_account_sid': twilio_config['TWILIO_ACCOUNT_SID'],
        'twilio_auth_token': twilio_config['TWILIO_AUTH_TOKEN'],
        'twilio_phone_number': twilio_config['TWILIO_PHONE_NUMBER']
    })


@login_required
@require_POST
def change_password_view(request):
    current = request.POST.get('current_password', '')
    new_pwd = request.POST.get('new_password', '')
    confirm = request.POST.get('confirm_password', '')
    user = request.user
    if not user.check_password(current):
        messages.error(request, 'Current password is incorrect.')
    elif new_pwd != confirm:
        messages.error(request, 'New passwords do not match.')
    elif len(new_pwd) < 8:
        messages.error(request, 'Password must be at least 8 characters.')
    else:
        user.set_password(new_pwd)
        user.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Password updated successfully!')
    return redirect('settings')


@login_required
def delete_account_view(request):
    user = request.user
    user.delete()
    logout(request)
    messages.success(request, 'Your account has been deleted.')
    return redirect('login')


from django.contrib.auth import login

def google_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, 'Google login failed: Email is empty.')
            return redirect('login')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            username = email.split('@')[0]
            if User.objects.filter(username=email).exists():
                user = User.objects.get(username=email)
            else:
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    first_name=username.capitalize(),
                    last_name='User',
                    role='user'
                )
        login(request, user)
        messages.success(request, f'Welcome, {user.first_name}! Logged in via Google.')
        return redirect('dashboard')
    return redirect('login')
