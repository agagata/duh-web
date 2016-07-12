import re

from django.db import models
from django.utils.html import format_html
from django.utils import timezone


class SPONSOR_LEVELS:
    H1 = 'h1'
    H2 = 'h2'
    H3 = 'h3'
    PARTNER = 'partner'

    choices = [
        (H1, '<h1>'),
        (H2, '<h2>'),
        (H3, '<h3>'),
        (PARTNER, 'Partner')
    ]


class SponsorQueryset(models.QuerySet):
    def h1(self):
        return self._by_level(SPONSOR_LEVELS.H1)

    def h2(self):
        return self._by_level(SPONSOR_LEVELS.H2)
        
    def h3(self):
        return self._by_level(SPONSOR_LEVELS.H3)

    def partner(self):
        return self._by_level(SPONSOR_LEVELS.PARTNER)

    def _by_level(self, level):
        return self.filter(level=level).order_by('?')

    def live(self):
        return self.filter(is_live=True)


class Sponsor(models.Model):
    LEVELS = SPONSOR_LEVELS

    level = models.CharField(max_length=20, choices=LEVELS.choices)
    name = models.CharField(max_length=200)
    description = models.TextField(
        blank=True, help_text="Use `[[link text]]` to create a link to the sponsor's URL.")
    logo = models.ImageField(blank=True, upload_to='sponsors/%Y/')
    url = models.URLField(blank=True)
    created_on = models.DateTimeField(default=timezone.now, editable=False)
    is_live = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)

    objects = SponsorQueryset.as_manager()

    def __str__(self):
        return self.name

    @property
    def linkified_description(self):
        """
        Replaces [[foo]] with <a href="{{ self.url }}">foo</a>.
        Also supports the [[http://example.com|foo]] syntax to generate
        <a href="http://example.com">foo</a>
        """
        links = []
        def linkify(matchobj, links=links):
            if '|' in matchobj.group(1):
                url = matchobj.group(1).split('|')
                link = format_html('<a href="{0}" target="_blank">{1}</a>', url[0], url[1])
            else:
                link = format_html('<a href="{0}" target="_blank">{1}</a>', self.url, matchobj.group(1))
            links.append(link)
            return '{%d}' % (len(links) - 1)

        fmt = re.sub(r'\[\[([^\]]+)\]\]', linkify, self.description)
        return format_html(fmt, *links)

    @property
    def logo_html(self):
        if self.logo:
            return format_html('<img class="logo" src="{0}" alt="{1}" title="{1}"/>', self.logo.url, self.name)
        return format_html('<span class="nologo">{0}</span>', self.name)
