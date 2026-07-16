from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from .models import CompanyStats, FAQItem
from .forms import ContactForm
from apps.projects.models import Project
from apps.seo.jsonld import organization_schema, faq_schema, webpage_schema, breadcrumb_schema, to_json


def homepage(request):
    stats = CompanyStats.load()
    # Key-projects bento: up to five, featured first, newest first. Broadened
    # beyond is_featured so the grid always fills even when few are flagged.
    key_projects = list(
        Project.objects.filter(is_published=True).order_by('-is_featured', '-year', 'order')[:5]
    )
    context = {
        'stats': stats,
        'key_projects': key_projects,
        'meta_title': _('Строительство и реконструкция железных дорог в Казахстане'),
        'meta_description': _('Проектирование, строительство и реконструкция железнодорожных путей для промышленных предприятий, портов и терминалов Казахстана. Более 15 лет опыта.'),
        'schema_json': to_json(organization_schema(request)),
        'page_id': 'home',
    }
    return render(request, 'core/homepage.html', context)


def about(request):
    stats = CompanyStats.load()
    context = {
        'stats': stats,
        'meta_title': _('О компании'),
        'meta_description': _('Казахстанская компания по строительству и реконструкции железнодорожных путей. Работаем с промышленными предприятиями, портами и логистическими терминалами.'),
        'schema_json': to_json(organization_schema(request)),
    }
    return render(request, 'core/about.html', context)


def faq(request):
    items = FAQItem.objects.filter(is_published=True)
    context = {
        'items': items,
        'meta_title': _('Часто задаваемые вопросы'),
        'meta_description': _('Ответы на часто задаваемые вопросы о строительстве железнодорожных путей, стоимости проектов и сроках работ.'),
        'schema_json': to_json(faq_schema(items)),
    }
    return render(request, 'core/faq.html', context)


def contacts(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            try:
                send_mail(
                    subject=f'Новая заявка от {inquiry.name}',
                    message=f'Имя: {inquiry.name}\nКомпания: {inquiry.company}\nТелефон: {inquiry.phone}\nEmail: {inquiry.email}\n\n{inquiry.message}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.INQUIRY_RECIPIENT_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass
            return redirect('core:contacts_success')
    else:
        form = ContactForm()
    meta_title = _('Контакты')
    meta_description = _('Свяжитесь с нами для получения консультации по строительству железнодорожных путей. Ответим в течение рабочего дня.')
    schemas = [
        webpage_schema(meta_title, meta_description, request, page_type='ContactPage'),
        breadcrumb_schema(request, [(_('Главная'), reverse('core:home')), (_('Контакты'), None)]),
    ]
    context = {
        'form': form,
        'meta_title': meta_title,
        'meta_description': meta_description,
        'schema_json': to_json(schemas),
    }
    return render(request, 'core/contacts.html', context)


def our_people(request):
    meta_title = _('Наши люди')
    meta_description = _('Команда специалистов по строительству и реконструкции железнодорожных путей в Казахстане.')
    schemas = [
        webpage_schema(meta_title, meta_description, request, page_type='AboutPage'),
        breadcrumb_schema(request, [(_('Главная'), reverse('core:home')), (_('Наши люди'), None)]),
    ]
    context = {
        'meta_title': meta_title,
        'meta_description': meta_description,
        'schema_json': to_json(schemas),
    }
    return render(request, 'core/our_people.html', context)


def our_leaders(request):
    meta_title = _('Руководство')
    meta_description = _('Руководящий состав компании Конкурент-Б — опытные управленцы в железнодорожной отрасли Казахстана.')
    schemas = [
        webpage_schema(meta_title, meta_description, request, page_type='AboutPage'),
        breadcrumb_schema(request, [(_('Главная'), reverse('core:home')), (_('Руководство'), None)]),
    ]
    context = {
        'meta_title': meta_title,
        'meta_description': meta_description,
        'schema_json': to_json(schemas),
    }
    return render(request, 'core/our_leaders.html', context)


def investors(request):
    meta_title = _('Инвесторам')
    meta_description = _('Информация для инвесторов о строительстве подъездных железнодорожных путей в Казахстане: выгоды, стоимость, окупаемость и порядок реализации проекта.')
    crumbs = [
        (_('Главная'), reverse('core:home')),
        (_('Инвесторам'), None),
    ]
    schemas = [
        webpage_schema(meta_title, meta_description, request),
        breadcrumb_schema(request, crumbs),
    ]
    context = {
        'meta_title': meta_title,
        'meta_description': meta_description,
        'schema_json': to_json(schemas),
    }
    return render(request, 'core/investors.html', context)


def construction_recommendations(request):
    meta_title = _('Рекомендации по строительству')
    meta_description = _('Как сократить сроки и уменьшить расходы при строительстве подъездного железнодорожного пути: практические рекомендации по срокам, договорам и материалам.')
    crumbs = [
        (_('Главная'), reverse('core:home')),
        (_('Инвесторам'), reverse('core:investors')),
        (_('Рекомендации по строительству'), None),
    ]
    schemas = [
        webpage_schema(meta_title, meta_description, request),
        breadcrumb_schema(request, crumbs),
    ]
    context = {
        'meta_title': meta_title,
        'meta_description': meta_description,
        'schema_json': to_json(schemas),
    }
    return render(request, 'core/construction_recommendations.html', context)


# ── Investor info pages — static skeletons, content is edited in templates ──
INVESTOR_PAGES = {
    'vybor-ploshchadki': {
        'template': 'core/investors/vybor-ploshchadki.html',
        'title': gettext_lazy('Выбор площадки под строительство объекта'),
        'meta_title': gettext_lazy('Выбор площадки под строительство объекта'),
        'meta_description': gettext_lazy('Что проверить при выборе площадки под подъездной железнодорожный путь: возможность врезки, расстояние до станции, землеотвод и факторы удорожания.'),
    },
    'spravochnik-terminov': {
        'template': 'core/investors/spravochnik-terminov.html',
        'title': gettext_lazy('Справочник терминов'),
        'meta_title': gettext_lazy('Справочник терминов'),
        'meta_description': gettext_lazy('Справочник терминов железнодорожного строительства и путевого хозяйства: балласт, верхнее строение пути, стрелочный перевод и другие понятия.'),
    },
    'tekhnologiya-stroitelstva': {
        'template': 'core/investors/tekhnologiya-stroitelstva.html',
        'title': gettext_lazy('Технология строительства'),
        'meta_title': gettext_lazy('Технология строительства'),
        'meta_description': gettext_lazy('Технология строительства железнодорожного пути: земляные работы, устройство верхнего строения пути и способы укладки рельсошпальной решётки.'),
    },
    'teo-proekta': {
        'template': 'core/investors/teo-proekta.html',
        'title': gettext_lazy('ТЭО проекта строительства подъездного жд-пути'),
        'meta_title': gettext_lazy('ТЭО проекта строительства подъездного жд-пути'),
        'meta_description': gettext_lazy('Технико-экономическое обоснование проекта строительства подъездного железнодорожного пути.'),
    },
    'etapy-stroitelstva': {
        'template': 'core/investors/etapy-stroitelstva.html',
        'title': gettext_lazy('Этапы строительства жд-пути'),
        'meta_title': gettext_lazy('Этапы строительства жд-пути'),
        'meta_description': gettext_lazy('Этапы строительства подъездного железнодорожного пути: подготовительные и проектные работы, строительство и ввод в эксплуатацию, сроки и стоимость.'),
    },
}


def investor_page(request, slug):
    page = INVESTOR_PAGES.get(slug)
    if page is None:
        raise Http404
    crumbs = [
        (_('Главная'), reverse('core:home')),
        (_('Инвесторам'), reverse('core:investors')),
        (str(page['title']), None),
    ]
    meta_title = str(page['meta_title'])
    meta_description = str(page['meta_description'])
    schemas = [
        webpage_schema(meta_title, meta_description, request),
        breadcrumb_schema(request, crumbs),
    ]
    context = {
        'meta_title': meta_title,
        'meta_description': meta_description,
        'schema_json': to_json(schemas),
    }
    return render(request, page['template'], context)


def contacts_success(request):
    context = {
        'meta_title': _('Заявка принята'),
        'meta_description': _('Ваша заявка принята. Мы свяжемся с вами в течение рабочего дня.'),
        'meta_robots': 'noindex, follow',
    }
    return render(request, 'core/contacts_success.html', context)
