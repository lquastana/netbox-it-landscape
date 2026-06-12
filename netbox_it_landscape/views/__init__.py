from .base import BaseLandscapeView  # noqa: F401
from .crud import (  # noqa: F401
    ApplicationBulkDeleteView,
    ApplicationDeleteView,
    ApplicationEditView,
    ApplicationFlowBulkDeleteView,
    ApplicationFlowDeleteView,
    ApplicationFlowEditView,
    ApplicationFlowListView,
    ApplicationFlowView,
    ApplicationListView,
    ApplicationView,
    BusinessDomainBulkDeleteView,
    BusinessDomainDeleteView,
    BusinessDomainEditView,
    BusinessDomainListView,
    BusinessDomainView,
    BusinessProcessBulkDeleteView,
    BusinessProcessDeleteView,
    BusinessProcessEditView,
    BusinessProcessListView,
    BusinessProcessView,
)
from .landscape import (  # noqa: F401
    ApplicativeLandscapeView,
    BusinessLandscapeView,
    ComparisonLandscapeView,
    FluxLandscapeView,
    KpiLandscapeView,
)
from .wizard import SetupWizardView  # noqa: F401
