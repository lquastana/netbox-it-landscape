from django.urls import path
from netbox.views.generic import ObjectChangeLogView, ObjectJournalView

from . import models, views

urlpatterns = (

    # Vues cartographiques
    path('synthese/', views.KpiLandscapeView.as_view(), name='kpi_landscape'),
    path('metier/', views.BusinessLandscapeView.as_view(), name='business_landscape'),
    path('applicatif/', views.ApplicativeLandscapeView.as_view(), name='applicative_landscape'),
    path('cartographie-flux/', views.FluxLandscapeView.as_view(), name='flux_landscape'),

    # Domaines métier
    path('domaines/', views.BusinessDomainListView.as_view(), name='businessdomain_list'),
    path('domaines/ajouter/', views.BusinessDomainEditView.as_view(), name='businessdomain_add'),
    path('domaines/supprimer/', views.BusinessDomainBulkDeleteView.as_view(), name='businessdomain_bulk_delete'),
    path('domaines/<int:pk>/', views.BusinessDomainView.as_view(), name='businessdomain'),
    path('domaines/<int:pk>/modifier/', views.BusinessDomainEditView.as_view(), name='businessdomain_edit'),
    path('domaines/<int:pk>/supprimer/', views.BusinessDomainDeleteView.as_view(), name='businessdomain_delete'),
    path('domaines/<int:pk>/journal-modifications/', ObjectChangeLogView.as_view(), name='businessdomain_changelog', kwargs={'model': models.BusinessDomain}),
    path('domaines/<int:pk>/journal/', ObjectJournalView.as_view(), name='businessdomain_journal', kwargs={'model': models.BusinessDomain}),

    # Processus métier
    path('processus/', views.BusinessProcessListView.as_view(), name='businessprocess_list'),
    path('processus/ajouter/', views.BusinessProcessEditView.as_view(), name='businessprocess_add'),
    path('processus/supprimer/', views.BusinessProcessBulkDeleteView.as_view(), name='businessprocess_bulk_delete'),
    path('processus/<int:pk>/', views.BusinessProcessView.as_view(), name='businessprocess'),
    path('processus/<int:pk>/modifier/', views.BusinessProcessEditView.as_view(), name='businessprocess_edit'),
    path('processus/<int:pk>/supprimer/', views.BusinessProcessDeleteView.as_view(), name='businessprocess_delete'),
    path('processus/<int:pk>/journal-modifications/', ObjectChangeLogView.as_view(), name='businessprocess_changelog', kwargs={'model': models.BusinessProcess}),
    path('processus/<int:pk>/journal/', ObjectJournalView.as_view(), name='businessprocess_journal', kwargs={'model': models.BusinessProcess}),

    # Applications
    path('applications/', views.ApplicationListView.as_view(), name='application_list'),
    path('applications/ajouter/', views.ApplicationEditView.as_view(), name='application_add'),
    path('applications/supprimer/', views.ApplicationBulkDeleteView.as_view(), name='application_bulk_delete'),
    path('applications/<int:pk>/', views.ApplicationView.as_view(), name='application'),
    path('applications/<int:pk>/modifier/', views.ApplicationEditView.as_view(), name='application_edit'),
    path('applications/<int:pk>/supprimer/', views.ApplicationDeleteView.as_view(), name='application_delete'),
    path('applications/<int:pk>/journal-modifications/', ObjectChangeLogView.as_view(), name='application_changelog', kwargs={'model': models.Application}),
    path('applications/<int:pk>/journal/', ObjectJournalView.as_view(), name='application_journal', kwargs={'model': models.Application}),

    # Flux applicatifs
    path('flux/', views.ApplicationFlowListView.as_view(), name='applicationflow_list'),
    path('flux/ajouter/', views.ApplicationFlowEditView.as_view(), name='applicationflow_add'),
    path('flux/supprimer/', views.ApplicationFlowBulkDeleteView.as_view(), name='applicationflow_bulk_delete'),
    path('flux/<int:pk>/', views.ApplicationFlowView.as_view(), name='applicationflow'),
    path('flux/<int:pk>/modifier/', views.ApplicationFlowEditView.as_view(), name='applicationflow_edit'),
    path('flux/<int:pk>/supprimer/', views.ApplicationFlowDeleteView.as_view(), name='applicationflow_delete'),
    path('flux/<int:pk>/journal-modifications/', ObjectChangeLogView.as_view(), name='applicationflow_changelog', kwargs={'model': models.ApplicationFlow}),
    path('flux/<int:pk>/journal/', ObjectJournalView.as_view(), name='applicationflow_journal', kwargs={'model': models.ApplicationFlow}),
)
