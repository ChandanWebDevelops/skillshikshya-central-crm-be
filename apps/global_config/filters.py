from rest_framework.filters import BaseFilterBackend


class BranchFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        branch_field = getattr(view, 'branch_field', 'branch')
        user_branch = getattr(request.user, 'branch', None)

        if request.user.is_staff or request.user.is_superuser:
            branch_id = request.query_params.get('branch_id')
            if branch_id:
                filter_kwargs = {f'{branch_field}_id': branch_id}
                return queryset.filter(**filter_kwargs)
            return queryset

        if user_branch:
            filter_kwargs = {branch_field: user_branch}
            return queryset.filter(**filter_kwargs)

        return queryset
