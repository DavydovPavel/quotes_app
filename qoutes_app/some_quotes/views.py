import random
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.db.models import Count, F, Sum
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Quote, Source
from .forms import QuoteForm, SourceForm


def random_quote(request):
    total_weight = Quote.objects.aggregate(total=Sum('weight'))['total'] or 0
    if total_weight > 0:
        random_value = random.randint(1, total_weight)
        cumulative_weight = 0
        quotes = Quote.objects.all()
        
        for quote in quotes:
            cumulative_weight += quote.weight
            if cumulative_weight >= random_value:
                selected_quote = quote
                break
    else:
        selected_quote = None
    
    if selected_quote:
        selected_quote.views_count += 1
        selected_quote.save()
    
    return render(request, 'random_quote.html', {
        'quote': selected_quote,
        'add_quote_form': QuoteForm(),
        'add_source_form': SourceForm(),
    })

@require_POST
def like_quote(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    action = request.POST.get(action)

    if action == 'like':
        quote.likes += 1
    elif action == 'dislike':
        quote.dislikes += 1
    
    quote.save()
    return JsonResponse({
        'likes': quote.likes,
        'dislikes': quote.dislikes,
        'rating': quote.rating(),
    })

def add_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Цитата успешно добавлена!')
            return redirect('random_quote')
        else:
            messages.error(request, 'Ошибка при добавлении цитаты')
    return redirect('random_quote')

def add_source(request):
    if request.method=='POST':
        form = SourceForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Источник успешно добавлен!')
            except IntegrityError:
                messages.error(request, 'Источник с таким названием уже существует!')
        else:
            messages.error(request, 'Ошибка при добавлении источника')
    return redirect('random_quote')

def popular_quotes(request):
    quotes_list = Quote.objects.annotate(
        rating=F('likes') - F('dislikes')
    ).order_by('-rating')

    paginator = Paginator(quotes_list, 10)
    page = request.GET.get('page')
    try:
        quotes = paginator.page(page)
    except PageNotAnInteger:
        quotes = paginator.page(1)
    except EmptyPage:
        quotes = paginator.page(paginator.num_pages)
    
    return render(request, 'popular_quotes.html', {
        'quotes': quotes,
    })

def all_quotes(request):
    quotes_list = Quote.objects.all().order_by('-created_at')
    paginator = Paginator(quotes_list, 10)
    page = request.GET.get('page')
    
    try:
        quotes = paginator.page(page)
    except PageNotAnInteger:
        quotes = paginator.page(1)
    except EmptyPage:
        quotes = paginator.page(paginator.num_pages)
    
    return render(request, 'all_quotes.html', {
        'quotes': quotes,
    })

def dashboard(request):
    total_quotes = Quote.objects.count()
    total_sources = Source.objects.count()
    total_views = Quote.objects.aggregate(total=Sum('views_count'))['total'] or 0
    total_likes = Quote.objects.aggregate(total=Sum('likes'))['total'] or 0
    
    popular_sources = Source.objects.annotate(
        total_quotes=Count('quotes'),
        total_likes=Sum('quotes__likes')
    ).order_by('-total_likes')[:5]
    
    return render(request, 'dashboard.html', {
        'total_quotes': total_quotes,
        'total_sources': total_sources,
        'total_views': total_views,
        'total_likes': total_likes,
        'popular_sources': popular_sources,
    })