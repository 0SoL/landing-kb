from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from .models import CompanyStats, FAQItem
from .forms import ContactForm
from apps.projects.models import Project
from apps.articles.models import Article
from apps.seo.jsonld import organization_schema, faq_schema, webpage_schema, breadcrumb_schema, to_json


def homepage(request):
    stats = CompanyStats.load()
    featured_projects = Project.objects.filter(is_featured=True, is_published=True)[:3]
    latest_news = Article.objects.filter(is_published=True, category__slug='novosti')[:3]
    context = {
        'stats': stats,
        'featured_projects': featured_projects,
        'latest_news': latest_news,
        'meta_title': 'Строительство и реконструкция железных дорог в Казахстане',
        'meta_description': 'Проектирование, строительство и реконструкция железнодорожных путей для промышленных предприятий, портов и терминалов Казахстана. Более 15 лет опыта.',
        'schema_json': to_json(organization_schema(request)),
        'page_id': 'home',
    }
    return render(request, 'core/homepage.html', context)


def about(request):
    stats = CompanyStats.load()
    context = {
        'stats': stats,
        'meta_title': 'О компании — РЖД-Инфра Казахстан',
        'meta_description': 'Казахстанская компания по строительству и реконструкции железнодорожных путей. Работаем с промышленными предприятиями, портами и логистическими терминалами.',
        'schema_json': to_json(organization_schema(request)),
    }
    return render(request, 'core/about.html', context)


def faq(request):
    items = FAQItem.objects.filter(is_published=True)
    context = {
        'items': items,
        'meta_title': 'Часто задаваемые вопросы — РЖД-Инфра Казахстан',
        'meta_description': 'Ответы на часто задаваемые вопросы о строительстве железнодорожных путей, стоимости проектов и сроках работ.',
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
    context = {
        'form': form,
        'meta_title': 'Контакты — РЖД-Инфра Казахстан',
        'meta_description': 'Свяжитесь с нами для получения консультации по строительству железнодорожных путей. Ответим в течение рабочего дня.',
    }
    return render(request, 'core/contacts.html', context)


def our_people(request):
    context = {
        'meta_title': 'Наши люди — Конкурент-Б',
        'meta_description': 'Команда специалистов по строительству и реконструкции железнодорожных путей в Казахстане.',
    }
    return render(request, 'core/our_people.html', context)


def our_leaders(request):
    context = {
        'meta_title': 'Руководство — Конкурент-Б',
        'meta_description': 'Руководящий состав компании Конкурент-Б — опытные управленцы в железнодорожной отрасли Казахстана.',
    }
    return render(request, 'core/our_leaders.html', context)


def investors(request):
    meta_title = 'Инвесторам — Конкурент-Б'
    meta_description = 'Информация для инвесторов о строительстве подъездных железнодорожных путей в Казахстане: выгоды, стоимость, окупаемость и порядок реализации проекта.'
    crumbs = [
        ('Главная', reverse('core:home')),
        ('Инвесторам', None),
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
    meta_title = 'Рекомендации по строительству — Конкурент-Б'
    meta_description = 'Как сократить сроки и уменьшить расходы при строительстве подъездного железнодорожного пути: практические рекомендации по срокам, договорам и материалам.'
    crumbs = [
        ('Главная', reverse('core:home')),
        ('Инвесторам', reverse('core:investors')),
        ('Рекомендации по строительству', None),
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
        'title': 'Выбор площадки под строительство объекта',
        'meta_title': 'Выбор площадки под строительство объекта — Конкурент-Б',
        'meta_description': 'Что проверить при выборе площадки под подъездной железнодорожный путь: возможность врезки, расстояние до станции, землеотвод и факторы удорожания.',
    },
    'spravochnik-terminov': {
        'template': 'core/investors/spravochnik-terminov.html',
        'title': 'Справочник терминов',
        'meta_title': 'Справочник терминов — Конкурент-Б',
        'meta_description': 'Справочник терминов железнодорожного строительства и путевого хозяйства: балласт, верхнее строение пути, стрелочный перевод и другие понятия.',
    },
    'tekhnologiya-stroitelstva': {
        'template': 'core/investors/tekhnologiya-stroitelstva.html',
        'title': 'Технология строительства',
        'meta_title': 'Технология строительства — Конкурент-Б',
        'meta_description': 'Технология строительства железнодорожного пути: земляные работы, устройство верхнего строения пути и способы укладки рельсошпальной решётки.',
    },
    'teo-proekta': {
        'template': 'core/investors/teo-proekta.html',
        'title': 'ТЭО проекта строительства подъездного жд-пути',
        'meta_title': 'ТЭО проекта строительства подъездного жд-пути — Конкурент-Б',
        'meta_description': 'Технико-экономическое обоснование проекта строительства подъездного железнодорожного пути.',
    },
    'etapy-stroitelstva': {
        'template': 'core/investors/etapy-stroitelstva.html',
        'title': 'Этапы строительства жд-пути',
        'meta_title': 'Этапы строительства жд-пути — Конкурент-Б',
        'meta_description': 'Этапы строительства подъездного железнодорожного пути: подготовительные и проектные работы, строительство и ввод в эксплуатацию, сроки и стоимость.',
    },
}


def investor_page(request, slug):
    page = INVESTOR_PAGES.get(slug)
    if page is None:
        raise Http404
    crumbs = [
        ('Главная', reverse('core:home')),
        ('Инвесторам', reverse('core:investors')),
        (page['title'], None),
    ]
    schemas = [
        webpage_schema(page['meta_title'], page['meta_description'], request),
        breadcrumb_schema(request, crumbs),
    ]
    context = {
        'meta_title': page['meta_title'],
        'meta_description': page['meta_description'],
        'schema_json': to_json(schemas),
    }
    return render(request, page['template'], context)


def contacts_success(request):
    context = {
        'meta_title': 'Заявка принята — РЖД-Инфра Казахстан',
        'meta_description': 'Ваша заявка принята. Мы свяжемся с вами в течение рабочего дня.',
    }
    return render(request, 'core/contacts_success.html', context)
