from netbox.search import SearchIndex, register_search

from .models import Application, ApplicationFlow, BusinessDomain, BusinessProcess


@register_search
class BusinessDomainIndex(SearchIndex):
    model = BusinessDomain
    fields = (
        ('name', 100),
        ('description', 500),
    )
    display_attrs = ('site', 'description')


@register_search
class BusinessProcessIndex(SearchIndex):
    model = BusinessProcess
    fields = (
        ('name', 100),
        ('description', 500),
    )
    display_attrs = ('domain', 'description')


@register_search
class ApplicationIndex(SearchIndex):
    model = Application
    fields = (
        ('name', 100),
        ('trigramme', 60),
        ('description', 500),
        ('editor', 300),
        ('hosting', 300),
    )
    display_attrs = ('trigramme', 'editor', 'criticality')


@register_search
class ApplicationFlowIndex(SearchIndex):
    model = ApplicationFlow
    fields = (
        ('flow_id', 60),
        ('protocol', 200),
        ('message_type', 200),
        ('eai', 300),
        ('description', 500),
    )
    display_attrs = ('protocol', 'message_type', 'eai')
