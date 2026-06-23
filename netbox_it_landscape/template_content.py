from netbox.plugins import PluginTemplateExtension

from .models import Application, ApplicationFlow, BusinessDomain


class ServerApplicationsPanel(PluginTemplateExtension):
    """Applications panel on VM and device detail pages."""
    models = ['virtualization.virtualmachine', 'dcim.device']

    def right_page(self):
        obj = self.context['object']
        if obj._meta.model_name == 'virtualmachine':
            applications = Application.objects.filter(virtual_machines=obj)
        else:
            applications = Application.objects.filter(devices=obj)
        applications = applications.prefetch_related('processes__domain__site')
        return self.render('netbox_it_landscape/inc/applications_panel.html', extra_context={
            'applications': applications,
        })


class SiteLandscapePanel(PluginTemplateExtension):
    """IT Landscape panel on Site detail pages."""
    models = ['dcim.site']

    def right_page(self):
        site = self.context['object']
        domain_count = BusinessDomain.objects.filter(site=site).count()
        application_count = Application.objects.filter(processes__domain__site=site).distinct().count()
        flow_count = ApplicationFlow.objects.filter(site=site).count()
        if not (domain_count or application_count or flow_count):
            return ''
        return self.render('netbox_it_landscape/inc/site_panel.html', extra_context={
            'domain_count': domain_count,
            'application_count': application_count,
            'flow_count': flow_count,
            'site': site,
        })


template_extensions = [
    ServerApplicationsPanel,
    SiteLandscapePanel,
]
