from core.models import ObjectType
from users.models import ObjectPermission


def grant_permission(user, model, *actions):
    """
    Grant NetBox object permissions (the NetBox auth backend ignores plain
    Django model permissions, ObjectPermission records are required).
    """
    permission = ObjectPermission.objects.create(
        name=f'test-{model._meta.app_label}-{model._meta.model_name}-{"-".join(actions)}',
        actions=list(actions),
    )
    permission.object_types.add(ObjectType.objects.get_for_model(model))
    permission.users.add(user)
    return permission
