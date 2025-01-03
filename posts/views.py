from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from posts.forms import PostForm
from posts.models import Post, Object3DFile, MediaFile


def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            media_files = request.FILES.getlist('media_files')
            for media in media_files:
                MediaFile.objects.create(post=post, file=media)

            object_3d_files = request.FILES.getlist('object_3d_files')
            for obj in object_3d_files:
                Object3DFile.objects.create(post=post, file=obj)

            return redirect('post_list')
    else:
        form = PostForm()

    return render(request, 'posts_html/create_post.html', {'form': form})


def post_list(request):
    posts = Post.objects.all()
    return render(request, 'posts_html/post_list.html', {'posts': posts})


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    media_files = post.media_files.all()  # Отримуємо всі медіа файли для цього посту
    object_3d_files = post.object_3d_files.all()  # Отримуємо всі 3D файли для цього посту
    return render(request, 'posts_html/post_detail.html', {
        'post': post,
        'media_files': media_files,
        'object_3d_files': object_3d_files
    })
