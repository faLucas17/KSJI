from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from django.contrib import messages

from core import models
from .models import Article, Category, Comment
from .forms import CommentForm

class ArticleListView(ListView):
    model = Article
    template_name = 'blog/blog_list.html'
    context_object_name = 'articles'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = Article.objects.filter(is_published=True)
        
        # Filtrer par catégorie si spécifié
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug, is_active=True)
            queryset = queryset.filter(category=category)
        
        # Filtrer par recherche si spécifié
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                models.Q(title__icontains=search_query) |
                models.Q(content__icontains=search_query) |
                models.Q(excerpt__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['recent_articles'] = Article.objects.filter(is_published=True)[:5]
        return context

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blog/blog_detail.html'
    context_object_name = 'article'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Article.objects.filter(is_published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        
        # Incrémenter le compteur de vues
        article.increment_views()
        
        # Ajouter les commentaires approuvés
        context['comments'] = article.comments.filter(is_approved=True)
        context['comment_form'] = CommentForm()
        context['related_articles'] = Article.objects.filter(
            is_published=True,
            category=article.category
        ).exclude(id=article.id)[:3]
        
        return context
    
    def post(self, request, *args, **kwargs):
        article = self.get_object()
        form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.save()
            
            messages.success(request, 'Votre commentaire a été soumis et sera publié après modération.')
            return redirect('blog_detail', slug=article.slug)
        
        # Si le formulaire n'est pas valide, réafficher la page avec les erreurs
        context = self.get_context_data()
        context['comment_form'] = form
        return render(request, self.template_name, context)