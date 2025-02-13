from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Post, User
from .forms import PostForm
from django.template.loader import render_to_string

from .models import Post, Comment
from .forms import CommentForm


def home(request):
    query = request.GET.get('q', '')
    author_id = request.GET.get('author', '')

    posts = Post.objects.filter(status='published').order_by('-created_at')

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query) |
            Q(created_at__icontains=query)
        )

    if author_id:
        posts = posts.filter(author_id=author_id)

    paginator = Paginator(posts, 3)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    authors = User.objects.filter(post__status='published').distinct()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('blog/filtered_posts.html', {'page_obj': page_obj})
        pagination_html = render_to_string('blog/pagination.html', {'page_obj': page_obj})
        return JsonResponse({'html': html, 'pagination': pagination_html})

    return render(request, 'blog/home.html', {
        'page_obj': page_obj,
        'authors': authors,
        'query': query,
        'author_id': author_id
    })



def about(request):
    return render(request, 'blog/about.html')



@login_required
def manage_posts(request):
    posts = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('blog/manage_posts_list.html', {'page_obj': page_obj}, request)
        pagination_html = render_to_string('blog/pagination.html', {'page_obj': page_obj}, request)
        return JsonResponse({'html': html, 'pagination': pagination_html})  # ✅ Sends only required parts

    return render(request, 'blog/manage_posts.html', {'page_obj': page_obj})



    
@login_required
def add_post(request):
    """
    Allows users to create a new blog post.
    """
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Post added successfully!")
            return redirect('manage_posts')
        else:
            messages.error(request, "Error adding post. Please check the form.")
    else:
        form = PostForm()
    
    return render(request, 'blog/add_post.html', {'form': form})

@login_required
def update_post(request, pk):
    """
    Allows users to update an existing blog post.
    """
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully!")
            return redirect('manage_posts')
        else:
            messages.error(request, "Error updating post. Please check the form.")
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/update_post.html', {'form': form})

@login_required
def delete_post(request, pk):
    """
    Allows users to delete their own posts. Admins can delete any post.
    """
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to delete this post.")

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('manage_posts')
    
    return HttpResponse(status=405)

def sidebar_context(request):
    """
    Provides context data for the sidebar including latest posts, authors, and search results.
    """
    latest_posts = Post.objects.filter(status='published').order_by('-created_at')[:5]
    authors = User.objects.filter(post__status='published').distinct()

    query = request.GET.get('q')
    search_results = None
    if query:
        search_results = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            status='published'
        )[:5]  # Limit search results

    return {
        'latest_posts': latest_posts,
        'authors': authors,
        'search_results': search_results,
    }

def author_posts(request, author_id):
    """
    Displays all posts by a specific author.
    """
    author = get_object_or_404(User, id=author_id)
    posts = Post.objects.filter(author=author, status='published').order_by('-created_at')

    return render(request, 'blog/author_posts.html', {'posts': posts, 'author': author})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all().order_by("-created_at")

    if request.method == "POST":
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                messages.success(request, "Your comment has been added!")
                return redirect("post_detail", pk=post.pk)
        else:
            messages.error(request, "You must be logged in to comment.")
            return redirect("login")

    else:
        form = CommentForm()

    return render(request, "blog/post_detail.html", {"post": post, "comments": comments, "form": form})

def filter_by_author(request, author_id):
    """
    Filters posts by a specific author and returns a partial HTML update.
    """
    author = get_object_or_404(User, id=author_id)
    posts = Post.objects.filter(author=author, status='published').order_by('-created_at')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('blog/filtered_posts.html', {'posts': posts, 'author': author})
        return JsonResponse({'html': html})

    return render(request, 'blog/author_posts.html', {'posts': posts, 'author': author})