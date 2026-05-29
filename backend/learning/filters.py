import django_filters
from .models import Course


class CourseFilter(django_filters.FilterSet):
    """Фильтр курсов: по уровню, преподавателю и диапазону дат создания."""

    level = django_filters.NumberFilter(field_name='level__id', label='ID уровня')
    teacher = django_filters.NumberFilter(
        field_name='teachers__id', label='ID преподавателя'
    )
    created_after = django_filters.DateFilter(
        field_name='created_at',
        method='filter_created_after',
        label='Создан после (YYYY-MM-DD)',
    )
    created_before = django_filters.DateFilter(
        field_name='created_at',
        method='filter_created_before',
        label='Создан до (YYYY-MM-DD)',
    )

    class Meta:
        model = Course
        fields = ['level', 'teacher']

    def filter_created_after(self, queryset, name, value):
        return queryset.filter(created_at__date__gte=value)

    def filter_created_before(self, queryset, name, value):
        return queryset.filter(created_at__date__lte=value)
