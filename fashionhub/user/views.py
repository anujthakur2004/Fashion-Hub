from django.contrib import messages
from django.shortcuts import render, redirect
from .models import User, Address
from django.core.exceptions import ValidationError
import re

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')

        # Basic validation
        if password != confirmpassword:
            messages.error(request, 'Passwords do not match')
            return render(request, 'register.html', {'error': 'Passwords do not match'})
        
        # Validate password strength
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long')
            return render(request, 'register.html', {'error': 'Password must be at least 8 characters long'})
        
        # Validate phone number
        if not re.match(r'^\d{10}$', phone):
            messages.error(request, 'Please enter a valid 10-digit phone number')
            return render(request, 'register.html', {'error': 'Please enter a valid 10-digit phone number'})

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'register.html', {'error': 'Username already exists'})
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'register.html', {'error': 'Email already exists'})

        try:
            # Create new user using your custom User model
            user = User.objects.create(
                username=username,
                email=email,
                password=password,  # Note: In a real application, you should hash this password
                phone=phone,
                gender=gender
            )
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'register.html', {'error': str(e)})
    
    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username, password=password)

            # Save user id in session to mark as logged in
            request.session['user_id'] = user.id
            messages.success(request, 'Login successful!')
            return redirect('profile')
        except User.DoesNotExist:
            messages.error(request, 'Invalid username or password')
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    
    return render(request, 'login.html')

def profile(request):
    user_obj = None
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user_obj = User.objects.get(id=user_id)
        except User.DoesNotExist:
            user_obj = None

    if not user_obj:
        messages.error(request, 'You must be logged in to view your profile')
        return redirect('login')

    # Prepare address parts for prefilling the address form
    address_parts = {
        'address1': '',
        'address2': '',
        'city': '',
        'state': '',
        'pincode': '',
    }
    if user_obj.address:
        parts = user_obj.address.split('||')
        # populate available parts safely
        for i, key in enumerate(['address1', 'address2', 'city', 'state', 'pincode']):
            if i < len(parts):
                address_parts[key] = parts[i]

    # Handle profile picture upload from the profile page
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        uploaded_file = request.FILES['profile_picture']
        try:
            user_obj.profile_picture = uploaded_file
            user_obj.save()
            messages.success(request, 'Profile picture updated')
            return redirect('profile')
        except Exception as e:
            messages.error(request, f'Could not upload image: {e}')
            return redirect('profile')

    # fetch user's addresses (new Address model)
    addresses = Address.objects.filter(user=user_obj).order_by('-is_primary', '-id')

    return render(request, 'profile.html', {'user': user_obj, 'address_parts': address_parts, 'addresses': addresses})

def logout(request):
    # Clear the session to log out
    request.session.flush()
    messages.success(request, 'You have been logged out')
    return redirect('login')

def update_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'You must be logged in to update your profile')
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('login')

    if request.method == 'POST':
        # template uses 'name' field for full name - accept both 'name' and 'username'
        username = request.POST.get('username') or request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')
        # Basic validation
        if password and password != confirmpassword:
            messages.error(request, 'Passwords do not match')
            return render(request, 'update_profile.html', {'user': user, 'error': 'Passwords do not match'})    
        # Validate phone number
        if not re.match(r'^\d{10}$', phone):
            messages.error(request, 'Please enter a valid 10-digit phone number')
            return render(request, 'update_profile.html', {'user': user, 'error': 'Please enter a valid 10-digit phone number'})
        user.username = username
        user.email = email
        user.phone = phone
        user.gender = gender
        if password:
            user.password = password  # Note: In a real application, you should hash this password      
        user.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('profile')
    return render(request, 'update_profile.html', {'user': user})

def update_address(request):
    
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'You must be logged in to update your address')
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('login')

    if request.method == 'POST':
        # Collect parts from the address form
        address1 = request.POST.get('address1', '').strip()
        address2 = request.POST.get('address2', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        pincode = request.POST.get('pincode', '').strip()

        # Store as a '||' separated string so we can prefill later
        combined = '||'.join([address1, address2, city, state, pincode])
        user.address = combined
        user.save()
        messages.success(request, 'Address updated successfully')
        return redirect('profile')
    return render(request, 'update_address.html', {'user': user})


def add_address(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'You must be logged in to add an address')
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('login')

    if request.method == 'POST':
        address1 = request.POST.get('address1', '').strip()
        address2 = request.POST.get('address2', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        pincode = request.POST.get('pincode', '').strip()

        is_primary = not Address.objects.filter(user=user).exists()

        addr = Address.objects.create(
            user=user,
            address1=address1,
            address2=address2,
            city=city,
            state=state,
            pincode=pincode,
            is_primary=is_primary,
        )
        messages.success(request, 'Address added')
        return redirect('profile')

    return redirect('profile')


def edit_address(request, addr_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'You must be logged in to edit an address')
        return redirect('login')

    try:
        addr = Address.objects.get(id=addr_id, user__id=user_id)
    except Address.DoesNotExist:
        messages.error(request, 'Address not found')
        return redirect('profile')

    if request.method == 'POST':
        addr.address1 = request.POST.get('address1', '').strip()
        addr.address2 = request.POST.get('address2', '').strip()
        addr.city = request.POST.get('city', '').strip()
        addr.state = request.POST.get('state', '').strip()
        addr.pincode = request.POST.get('pincode', '').strip()
        addr.save()
        messages.success(request, 'Address updated')
        return redirect('profile')

    return redirect('profile')


def delete_address(request, addr_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'You must be logged in to delete an address')
        return redirect('login')

    try:
        addr = Address.objects.get(id=addr_id, user__id=user_id)
        addr.delete()
        messages.success(request, 'Address deleted')
    except Address.DoesNotExist:
        messages.error(request, 'Address not found')

    return redirect('profile')

def change_password(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'You must be logged in to change your password')
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('login')

    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if user.password != current_password:
            messages.error(request, 'Current password is incorrect')
            return render(request, 'change_password.html', {'error': 'Current password is incorrect'})

        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match')
            return render(request, 'change_password.html', {'error': 'New passwords do not match'})

        user.password = new_password  # Note: In a real application, you should hash this password
        user.save()
        messages.success(request, 'Password changed successfully')
        return redirect('profile')

    return render(request, 'change_password.html')
