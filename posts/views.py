from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

from posts.forms import PostForm, EditPostForm
from posts.models import Post, Object3DFile, MediaFile, Comment


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
    post = get_object_or_404(Post, id=post_id)
    media_files = post.media_files.all()
    object_3d_files = post.object_3d_files.all()

    # Основні коментарі (без батьків)
    comments = post.comments.filter(parent=None).order_by('-created_at')

    # Відповіді на коментарі
    replies = post.comments.exclude(parent=None).order_by('created_at')

    return render(request, 'posts_html/post_detail.html', {
        'post': post,
        'media_files': media_files,
        'object_3d_files': object_3d_files,
        'comments': comments,
        'replies': replies  # Передаємо відповіді окремо
    })


@csrf_protect
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        post.delete()
        return redirect('post_list')  # Після видалення перенаправлення на головну

    return redirect('post_detail', post_id=post_id)


def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    existing_media_files = MediaFile.objects.filter(post=post)
    existing_object_files = Object3DFile.objects.filter(post=post)

    if request.method == 'POST':
        form = EditPostForm(
            request.POST, request.FILES, instance=post,
            existing_media_files=existing_media_files,
            existing_object_files=existing_object_files
        )
        if form.is_valid():
            form.save()

            # Отримуємо списки файлів, які потрібно залишити
            remaining_media_files = request.POST.getlist('existing_media_files')
            remaining_object_files = request.POST.getlist('existing_object_files')

            # Видаляємо файли, яких немає у списку залишених
            MediaFile.objects.filter(post=post).exclude(id__in=remaining_media_files).delete()
            Object3DFile.objects.filter(post=post).exclude(id__in=remaining_object_files).delete()

            # Додаємо нові файли
            for media in request.FILES.getlist('media_files'):
                MediaFile.objects.create(post=post, file=media)

            for obj in request.FILES.getlist('object_3d_files'):
                Object3DFile.objects.create(post=post, file=obj)

            return redirect('post_detail', post_id=post.id)
    else:
        form = EditPostForm(instance=post, existing_media_files=existing_media_files, existing_object_files=existing_object_files)

    return render(request, 'posts_html/edit_post.html', {
        'form': form,
        'existing_media_files': existing_media_files,
        'existing_object_files': existing_object_files,
    })


@login_required
def toggle_cube(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Перевіряємо, чи користувач вже поставив куб
    if request.user in post.likes.all():
        # Якщо користувач вже поставив куб, видаляємо його
        post.cubes -= 1
        post.likes.remove(request.user)
    else:
        # Якщо куб не поставлений, додаємо
        post.cubes += 1
        post.likes.add(request.user)

    post.save()

    # Перенаправляємо назад на деталі поста
    return redirect('post_detail', post_id=post.id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        content = request.POST.get("content")
        parent_id = request.POST.get("parent_id")  # Отримуємо ID батьківського коментаря (якщо це відповідь)
        parent = Comment.objects.get(id=parent_id) if parent_id else None

        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content,
            parent=parent  # Встановлюємо батьківський коментар
        )
        return redirect('post_detail', post_id=post.id)


@login_required
def toggle_cube_for_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        comment.cubes -= 1
    else:
        comment.likes.add(request.user)
        comment.cubes += 1
    comment.save()

    return JsonResponse({'success': True, 'cubes': comment.cubes})


@login_required
def delete_comment(request, comment_id):
    # Отримуємо коментар за ID
    comment = get_object_or_404(Comment, id=comment_id)

    # Перевіряємо, чи автор є тим самим, що і у коментаря
    if request.user == comment.author:
        comment.delete()  # Видаляємо коментар
        return redirect('post_detail', post_id=comment.post.id)  # Перенаправляємо на деталі поста
    else:
        return redirect('post_detail', post_id=comment.post.id)  # Якщо не автор, просто перенаправляємо


@login_required
def delete_reply(request, reply_id):
    # Отримуємо відповідь за ID
    reply = get_object_or_404(Comment, id=reply_id)

    # Перевіряємо, чи автор є тим самим, що і у відповіді
    if request.user == reply.author:
        reply.delete()  # Видаляємо відповідь
        return redirect('post_detail', post_id=reply.post.id)  # Перенаправляємо на деталі поста
    else:
        return redirect('post_detail', post_id=reply.post.id)  # Якщо не автор, просто перенаправляємо


