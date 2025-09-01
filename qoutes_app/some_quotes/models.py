from django.db import models
from django.core.exceptions import ValidationError

class Source(models.Model):    
    title = models.CharField(max_length=200, unique=True, verbose_name="Название")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title
    
    def quote_count(self):
        return self.quotes.count()
    
class Quote(models.Model):
    text = models.TextField(verbose_name="Текст цитаты")
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='quotes', verbose_name="Источник")
    weight = models.PositiveIntegerField(default=1, verbose_name="Вес")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    likes = models.PositiveIntegerField(default=0, verbose_name="Лайки")
    dislikes = models.PositiveIntegerField(default=0, verbose_name="Дизлайки")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('text', 'source')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.text[:50]}... - {self.source}"
    
    def clean(self):
        if self.pk is None:
            quote_count = Quote.objects.filter(source=self.source).count()
            if quote_count >= 3:
                raise ValidationError(f"У источника '{self.source}' уже максимальное количество цитат (3)")
            
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def rating(self):
        return self.likes - self.dislikes
    
    def like_percentage(self):
        total = self.likes + self.dislikes
        if total == 0:
            return 0
        return (self.likes / total) * 100