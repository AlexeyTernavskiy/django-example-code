# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import ProductModel, CommentModel


@admin.register(ProductModel)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'user', 'created')
    ordering = ('created', 'name',)
    list_filter = ('created',)


@admin.register(CommentModel)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment_text', 'product', 'user',)
    ordering = ('product', 'user',)
    list_filter = ('product', 'user',)
    search_fields = ('comment',)

    @staticmethod
    def comment_text(obj):
        if len(obj.comment) > 70:
            return '{0} ...'.format(obj.comment[:70])
        return obj.comment
