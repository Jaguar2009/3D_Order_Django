from django.contrib import admin

from posts.models import Post, MediaFile, Object3DFile, Comment
from users.models import User

admin.site.register(User)
admin.site.register(Post)
admin.site.register(MediaFile)
admin.site.register(Object3DFile)

admin.site.register(Comment)