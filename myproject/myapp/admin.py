from django.contrib import admin

# Register your models here.
from .models import Category,Post

class PostAdmin(admin.ModelAdmin):
    list_display = ['title','author','category','created_at']

admin.site.register(Category)
admin.site.register(Post,PostAdmin)
