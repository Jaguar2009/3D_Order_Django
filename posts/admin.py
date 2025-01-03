from django.contrib import admin

from posts.models import Post, MediaFile, Object3DFile
from users.models import User

admin.site.register(User)
admin.site.register(Post)
admin.site.register(MediaFile)
admin.site.register(Object3DFile)
