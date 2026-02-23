from django.contrib import admin

# Register your models here.
from .models import Category, Article, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ['name']}
    list_editable = ['is_active']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'published_date', 'is_published', 'views']
    list_filter = ['is_published', 'category', 'published_date']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ['title']}
    list_editable = ['is_published']
    readonly_fields = ['views']
    filter_horizontal = []
    date_hierarchy = 'published_date'
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'category', 'tags')
        }),
        ('Médias', {
            'fields': ('thumbnail',)
        }),
        ('Publication', {
            'fields': ('author', 'is_published')
        }),
        ('Statistiques', {
            'fields': ('views',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'article', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['name', 'email', 'content']
    list_editable = ['is_approved']
    actions = ['approve_comments']
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Approuver les commentaires sélectionnés"
    
