from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from .models import User, Address
import re


# ---------------- REGISTER ----------------
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        if password != confirmpassword:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            gender=gender
        )

        messages.success(request, 'Registration successful! Please log in.')
        return redirect('login')

    return render(request, 'register.html')



# ---------------- LOGIN ----------------
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('profile')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')


# ---------------- LOGOUT ----------------
def logout(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


# ---------------- PROFILE ----------------
@login_required(login_url='login')
def profile(request):
    user = request.user
    addresses = Address.objects.filter(user=user).order_by('-is_primary', '-id')

    # Handle profile picture upload
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        user.profile_picture = request.FILES['profile_picture']
        user.save()
        messages.success(request, 'Profile picture updated successfully.')
        return redirect('profile')

    return render(request, 'profile.html', {
        'user': user,
        'addresses': addresses,
    })


# ---------------- UPDATE PROFILE ----------------
@login_required(login_url='login')
def update_profile(request):
    user = request.user

    if request.method == 'POST':
        username = request.POST.get('username') or request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')

        if password and password != confirmpassword:
            messages.error(request, 'Passwords do not match')
            return redirect('profile')

        if phone and not re.match(r'^\d{10}$', phone):
            messages.error(request, 'Please enter a valid 10-digit phone number')
            return redirect('profile')

        user.username = username
        user.email = email
        if password:
            user.set_password(password)
        user.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'profile.html', {'user': user})


# ---------------- ADDRESS MANAGEMENT ----------------
@login_required(login_url='login')
def add_address(request):
    user = request.user
    if request.method == 'POST':
        address1 = request.POST.get('address1', '').strip()
        address2 = request.POST.get('address2', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        pincode = request.POST.get('pincode', '').strip()

        if not address1 or not city or not state or not pincode:
            messages.error(request, 'Please fill all required address fields.')
            return redirect('profile')

        is_primary = not Address.objects.filter(user=user).exists()

        Address.objects.create(
            user=user,
            address1=address1,
            address2=address2,
            city=city,
            state=state,
            pincode=pincode,
            is_primary=is_primary,
        )
        messages.success(request, 'Address added successfully!')
        return redirect('profile')

    return redirect('profile')


@login_required(login_url='login')
def edit_address(request, addr_id):
    address = get_object_or_404(Address, id=addr_id, user=request.user)

    if request.method == 'POST':
        address.address1 = request.POST.get('address1', '').strip()
        address.address2 = request.POST.get('address2', '').strip()
        address.city = request.POST.get('city', '').strip()
        address.state = request.POST.get('state', '').strip()
        address.pincode = request.POST.get('pincode', '').strip()
        address.save()
        messages.success(request, 'Address updated successfully!')
        return redirect('profile')

    return redirect('profile')


@login_required(login_url='login')
def delete_address(request, addr_id):
    try:
        address = Address.objects.get(id=addr_id, user=request.user)
        address.delete()
        messages.success(request, 'Address deleted successfully.')
    except Address.DoesNotExist:
        messages.error(request, 'Address not found.')

    return redirect('profile')

@login_required(login_url='login')
def update_address(request):
    """
    Updates the primary address directly from the profile page form.
    If no primary address exists, creates a new one.
    """
    user = request.user

    if request.method == 'POST':
        address1 = request.POST.get('address1', '').strip()
        address2 = request.POST.get('address2', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        pincode = request.POST.get('pincode', '').strip()

        if not address1 or not city or not state or not pincode:
            messages.error(request, 'Please fill all required address fields.')
            return redirect('profile')

        # Fetch or create a primary address
        address, created = Address.objects.get_or_create(
            user=user,
            is_primary=True,
            defaults={
                'address1': address1,
                'address2': address2,
                'city': city,
                'state': state,
                'pincode': pincode,
            }
        )

        if not created:
            # Update existing address
            address.address1 = address1
            address.address2 = address2
            address.city = city
            address.state = state
            address.pincode = pincode
            address.save()

        messages.success(request, 'Address updated successfully!')
        return redirect('profile')

    return redirect('profile')


# ---------------- CHANGE PASSWORD ----------------
@login_required(login_url='login')
def change_password(request):
    user = request.user
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('change_password')

        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('change_password')

        user.set_password(new_password)
        user.save()
        messages.success(request, 'Password changed successfully! Please log in again.')
        return redirect('login')

    return render(request, 'profile.html')
