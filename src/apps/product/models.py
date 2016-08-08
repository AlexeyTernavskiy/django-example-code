# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MinLengthValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel


@python_2_unicode_compatible
class ProductModel(TimeStampedModel):
    user = models.ForeignKey(User,
                             related_name='products',
                             verbose_name=_('User'), )
    name = models.CharField(max_length=100,
                            unique=True,
                            verbose_name=_('Name of product'), )
    slug = models.SlugField(max_length=100,
                            unique=True,
                            primary_key=True,
                            verbose_name=_('Url of product'))
    description = models.TextField(verbose_name=_('Description of product'), )
    price = models.DecimalField(verbose_name=_('Price of product'),
                                decimal_places=2,
                                max_digits=12,
                                validators=[MinValueValidator(Decimal('0.01'))], )

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ('-created',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:detail', args=[self.slug])


@python_2_unicode_compatible
class CommentModel(TimeStampedModel):
    user = models.ForeignKey(User,
                             related_name='comments',
                             verbose_name=_('User'),
                             blank=True,
                             null=True, )
    product = models.ForeignKey(ProductModel,
                                related_name='products',
                                verbose_name=_('Product'), )
    comment = models.TextField(verbose_name=_('Comment'),
                               validators=[MinLengthValidator(limit_value=3)], )

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        ordering = ('-created',)

    def __str__(self):
        return self.comment


@python_2_unicode_compatible
class LikeModel(models.Model):
    user = models.ForeignKey(User,
                             verbose_name=_('User'),
                             related_name='like', )
    product = models.ForeignKey(ProductModel,
                                verbose_name=_('Product'),
                                related_name='like', )

    class Meta:
        verbose_name = _('Like')
        verbose_name_plural = _('Likes')

    def __str__(self):
        return '{0} {1}'.format(self.user.username, self.product.name)
