from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, PostCreationForm
from django.contrib.auth import authenticate, login, logout
from .models import Post
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai  # Ensure you have the correct library installed

# Create your views here.

def home(request):
    name = 'Sai Shivamani'
    numbers = [1, 2, 3, 4, 5, 6]
    context = {'name': name, 'numbers': numbers}
    return render(request, 'myapp/home.html', context)

def userlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)  # Verify credentials
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            context = {'error': "Invalid username or password"}
            return render(request, 'myapp/userlogin.html', context)
    else:
        return render(request, 'myapp/userlogin.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            context = {'form': form, 'error': 'Invalid submission'}
            return render(request, 'myapp/register.html', context)
    else:
        form = UserRegistrationForm()
        return render(request, 'myapp/register.html', {'form': form})

def userlogout(request):
    logout(request)
    return redirect('userlogin')

def displayposts(request):
    post_list = Post.objects.all().order_by('-created_at')  # Get posts ordered by creation time
    context = {'post_list': post_list}
    return render(request, 'myapp/displayposts.html', context)

@login_required(login_url='userlogin')
def create_post(request):
    if request.method == 'POST':
        form = PostCreationForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('displayposts')
        else:
            context = {'form': form, 'error': 'Invalid post submission'}
            return render(request, 'myapp/create_post.html', context)
    else:
        form = PostCreationForm()
        return render(request, 'myapp/create_post.html', {'form': form})

def updatepost(request, id):
    post = Post.objects.get(pk=id)
    if request.method == 'POST':
        form = PostCreationForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('displayposts')
        else:
            context = {'form': form, 'error': 'Invalid form submission'}
            return render(request, 'myapp/updatepost.html', context)
    else:
        form = PostCreationForm(instance=post)
        return render(request, 'myapp/updatepost.html', {'form': form})

def deletepost(request, id):
    try:
        post = Post.objects.get(pk=id)
        post.delete()
        return redirect('displayposts')
    except Post.DoesNotExist:
        return HttpResponseBadRequest('<p>Bad Request! Post not found.</p> <a href="/">Click Here</a> to go to home page')

# Chatbot view with error handling
@csrf_exempt
def chatbot_view(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        if not prompt:
            return JsonResponse({'response': 'Prompt cannot be empty!'}, status=400)

        my_api_key_gemini = "API KEY" # update your api key here
        genai.configure(api_key=my_api_key_gemini)

        try:
            # Use a simple model like 'text-bison-001' instead of 'gemini-pro' if available
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)

            if response and hasattr(response, 'text'):
                return JsonResponse({'response': response.text}, status=200)
            else:
                return JsonResponse({'response': 'Gemini did not return any response.'}, status=500)
        except Exception as e:
            return JsonResponse({'response': f"An error occurred: {str(e)}"}, status=500)
    else:
        return JsonResponse({'response': 'Invalid request'}, status=400)
