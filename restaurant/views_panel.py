"""Generic control-panel views.

One list view, one form view, one toggle and one delete serve every model
in the section registry, so the panel covers the whole site without a view
per model. Permissions come from Django's own model permissions, which
means existing staff roles keep working unchanged.
"""
from django import forms
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import modelform_factory
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from . import panel
from .admin import RestaurantSettingsAdminForm
from .models import RestaurantSettings

PER_PAGE = 25


def _tune_widgets(form):
    """Native pickers beat free text for dates, times and colours.

    Applied after the form is built so it works for every model without a
    widget declaration per field.
    """
    for name, field in form.fields.items():
        if isinstance(field, forms.TimeField):
            field.widget = forms.TimeInput(attrs={'type': 'time'}, format='%H:%M')
        elif isinstance(field, forms.DateField):
            field.widget = forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        elif name.endswith('_color'):
            field.widget = forms.TextInput(attrs={'type': 'color'})
    return form


def _section_or_404(slug):
    section = panel.get_section(slug)
    if section is None:
        raise Http404('لا يوجد قسم بهذا الاسم.')
    return section


def _require(user, section, action):
    if not user.has_perm(panel.perm(section, action)):
        raise PermissionDenied


def _chrome(request, active, **extra):
    """Shared sidebar/topbar context for every panel page."""
    context = {
        'site': RestaurantSettings.load(),
        'nav_groups': panel.nav(request.user, active=active),
        'active_section': active,
        'user_name': request.user.get_full_name() or request.user.get_username(),
        'user_initial': (
            (request.user.get_full_name() or request.user.get_username()).strip()[:1] or '؟'
        ).upper(),
    }
    context.update(extra)
    return context


@staff_member_required
def section_list(request, slug):
    section = _section_or_404(slug)
    _require(request.user, section, 'view')

    queryset = section['model'].objects.all()
    if section.get('related'):
        queryset = queryset.select_related(*section['related'])
    queryset = queryset.order_by(*section['ordering'])

    query = request.GET.get('q', '').strip()
    if query and section['search']:
        matches = Q()
        for field in section['search']:
            matches |= Q(**{f'{field}__icontains': query})
        queryset = queryset.filter(matches)

    page = Paginator(queryset, PER_PAGE).get_page(request.GET.get('page'))
    rows = [
        {
            'object': item,
            'cells': [panel.cell(item, field) for field, _ in section['columns']],
            'edit_url': reverse('restaurant:panel_edit', args=[slug, item.pk]),
            'detail_url': (
                reverse(section['detail_url'], args=[getattr(item, section['detail_field'])])
                if section.get('detail_url') else ''
            ),
        }
        for item in page.object_list
    ]

    return render(request, 'restaurant/panel_list.html', _chrome(
        request, slug,
        section=section,
        section_slug=slug,
        headers=[label for _, label in section['columns']],
        rows=rows,
        page=page,
        query=query,
        total=queryset.count(),
        can_add=section.get('can_add') and request.user.has_perm(panel.perm(section, 'add')),
        can_change=request.user.has_perm(panel.perm(section, 'change')),
        can_delete=request.user.has_perm(panel.perm(section, 'delete')),
    ))


@staff_member_required
def section_form(request, slug, pk=None):
    section = _section_or_404(slug)
    model = section['model']

    if pk is None:
        _require(request.user, section, 'add')
        instance = None
    else:
        _require(request.user, section, 'change')
        instance = get_object_or_404(model, pk=pk)

    form_class = modelform_factory(model, fields=section.get('form_fields', '__all__'))

    if request.method == 'POST':
        form = _tune_widgets(form_class(request.POST, request.FILES, instance=instance))
        if form.is_valid():
            saved = form.save()
            messages.success(
                request,
                f'تم حفظ {section["singular"]}: {saved}.' if instance
                else f'تمت إضافة {section["singular"]}: {saved}.',
            )
            return redirect('restaurant:panel_list', slug=slug)
        messages.error(request, 'راجع الحقول المميزة بالأحمر.')
    else:
        form = _tune_widgets(form_class(instance=instance))

    return render(request, 'restaurant/panel_form.html', _chrome(
        request, slug,
        section=section,
        section_slug=slug,
        form=form,
        instance=instance,
        groups=[('', list(form))],
        can_delete=instance is not None and request.user.has_perm(panel.perm(section, 'delete')),
    ))


@staff_member_required
@require_POST
def section_toggle(request, slug, pk):
    """Flip one boolean straight from the list, e.g. hide a dish."""
    section = _section_or_404(slug)
    _require(request.user, section, 'change')

    field = request.POST.get('field', '')
    if field not in section['toggles']:
        raise PermissionDenied

    item = get_object_or_404(section['model'], pk=pk)
    setattr(item, field, not getattr(item, field))
    item.save(update_fields=[field, 'updated_at'])
    messages.success(request, f'تم تحديث: {item}.')
    return redirect(_back(request, slug))


@staff_member_required
@require_POST
def section_delete(request, slug, pk):
    section = _section_or_404(slug)
    _require(request.user, section, 'delete')

    item = get_object_or_404(section['model'], pk=pk)
    label = str(item)
    try:
        item.delete()
    except Exception:
        # A category still holding dishes is protected at the database level.
        messages.error(request, f'تعذر حذف {label} لأن عناصر أخرى مرتبطة به.')
        return redirect(_back(request, slug))

    messages.success(request, f'تم حذف {label}.')
    return redirect('restaurant:panel_list', slug=slug)


@staff_member_required
def site_settings(request):
    section = {'title': 'إعدادات الموقع', 'singular': 'الإعدادات'}
    if not request.user.has_perm('restaurant.change_restaurantsettings'):
        raise PermissionDenied

    instance = RestaurantSettings.load()
    if request.method == 'POST':
        form = _tune_widgets(RestaurantSettingsAdminForm(request.POST, request.FILES, instance=instance))
        if form.is_valid():
            form.save()
            messages.success(request, 'تم حفظ إعدادات الموقع.')
            return redirect('restaurant:panel_settings')
        messages.error(request, 'راجع الحقول المميزة بالأحمر.')
    else:
        form = _tune_widgets(RestaurantSettingsAdminForm(instance=instance))

    # Group the fields the way the landing page reads, not the model order.
    grouped = []
    used = set()
    for title, names in panel.SETTINGS_GROUPS:
        fields = [form[name] for name in names if name in form.fields]
        used.update(name for name in names if name in form.fields)
        if fields:
            grouped.append((title, fields))
    leftovers = [form[name] for name in form.fields if name not in used]
    if leftovers:
        grouped.append(('أخرى', leftovers))

    return render(request, 'restaurant/panel_form.html', _chrome(
        request, 'settings',
        section=section,
        section_slug='settings',
        form=form,
        instance=instance,
        groups=grouped,
        is_settings=True,
        can_delete=False,
    ))


def _back(request, slug):
    """Return to the list the action came from, keeping search and page."""
    base = reverse('restaurant:panel_list', args=[slug])
    params = [
        f'{key}={request.POST.get(key)}'
        for key in ('q', 'page') if request.POST.get(key)
    ]
    return f'{base}?{"&".join(params)}' if params else base
