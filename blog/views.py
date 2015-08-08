from django.shortcuts import render
from .models import Post
from django.utils import timezone
import datetime
from django.shortcuts import render, get_object_or_404
from .forms import PostForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.template import Context, loader

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    archive_dict = get_post_archive()
    return render(request, 'blog/post_list.html', {'posts': posts, 'archive_dict': archive_dict })


def post_detail(request, pk):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    post = get_object_or_404(Post, pk=pk)
    archive_dict = get_post_archive()
    return render(request, 'blog/post_detail.html', {'post': post, 'posts': posts, 'archive_dict': archive_dict })

@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog.views.post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog.views.post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('blog.views.post_detail', pk=pk)

@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('blog.views.post_list')
    
def get_post_archive():
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    now = datetime.datetime.now()

    #create a dict with the years and months of posts
    post_dict = {}

    month_list = [
        'dummy',
        'January',
        'February',
        'March',
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December'
    ]
    for i in range(posts[0].published_date.year, posts[len(posts)-1].published_date.year-1, -1):
        post_dict[i] = {}
        for month in range(1, 13):
            post_dict[i][month_list[month]] = []
    for archive_post in posts:
        post_dict[archive_post.published_date.year][month_list[archive_post.published_date.month]].append(archive_post)

    #this is necessary for the years to be sorted
    post_sorted_keys = list(reversed(sorted(post_dict.keys())))
    list_posts = []
    for key in post_sorted_keys:
        adict = {key:post_dict[key]}
        list_posts.append(adict)
    print(list_posts)
    return list_posts

