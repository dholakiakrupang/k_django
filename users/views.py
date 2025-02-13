from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from .forms import UserRegistrationForm, ProfileUpdateForm
from .models import Profile
from django.http import JsonResponse

# User Registration View
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)  # Include request.FILES
        if form.is_valid():
            user = form.save()
            profile_picture = form.cleaned_data.get('profile_picture')

            # Create or update the Profile
            profile, created = Profile.objects.get_or_create(user=user)
            if profile_picture:
                profile.profile_picture = profile_picture
            profile.save()

            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})


# Profile View
@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)  # Ensure profile exists
    user_form = UserRegistrationForm(instance=request.user)
    profile_form = ProfileUpdateForm(instance=profile)

    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')

    return render(request, 'users/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


# Profile Update View (Optional if profile updates are separate from profile view)
@login_required
def profile_update(request):
    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name", "")
        user.last_name = request.POST.get("last_name", "")
        user.email = request.POST.get("email", "")
        user.save()

        profile = user.profile
        profile.bio = request.POST.get("bio", "")

        if "profile_picture" in request.FILES:
            profile.profile_picture = request.FILES["profile_picture"]
        
        profile.save()

        return JsonResponse({"success": True, "profile_picture_url": profile.profile_picture.url if profile.profile_picture else None})

    return render(request, "blog/profile.html")
# Logout View
def logout(request):
    auth_logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('blog-home')  # Redirect to the homepage or any desired page after logout
