from django.shortcuts import render
from .models import Post
from django.utils import timezone
import datetime
from django.shortcuts import render, get_object_or_404
from .forms import PostForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.template import Context, loader
from collections import OrderedDict


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    archive_dict = get_post_archive()
    return render(request, 'blog/post_list.html', {'posts': posts, 'archive_dict': archive_dict})


def post_detail(request, pk):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    post = get_object_or_404(Post, pk=pk)
    archive_dict = get_post_archive()
    return render(request, 'blog/post_detail.html', {'post': post, 'posts': posts, 'archive_dict': archive_dict})


@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
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
            return redirect('post_detail', pk=post.pk)
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
    return redirect('post_detail', pk=pk)


@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('post_list')


def get_post_archive():
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')

    post_dict = OrderedDict()

    month_dict = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December'
    }

    for i in range(posts[0].published_date.year, posts[len(posts)-1].published_date.year-1, -1):
        post_dict[i] = OrderedDict()
        for month in range(1, 13):
            post_dict[i][month_dict[month]] = []

    for archive_post in posts:
        post_dict[archive_post.published_date.year][month_dict[archive_post.published_date.month]].append(archive_post)

    list_posts = []
    for key in post_dict:
        adict = {key:post_dict[key]}
        list_posts.append(adict)

    return list_posts

