from django.http import HttpResponse

# AI crawlers that get an explicit Allow on top of the general rule
AI_BOTS = [
    'GPTBot',
    'OAI-SearchBot',
    'ChatGPT-User',
    'Google-Extended',
    'PerplexityBot',
    'Perplexity-User',
    'ClaudeBot',
    'Claude-Web',
    'anthropic-ai',
    'CCBot',
    'Applebot-Extended',
    'meta-externalagent',
]


def robots_txt(request):
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin/',
        '',
    ]
    for bot in AI_BOTS:
        lines += [f'User-agent: {bot}', 'Allow: /', '']
    lines += [
        f'Sitemap: {request.build_absolute_uri("/sitemap.xml")}',
        f'LLMs: {request.build_absolute_uri("/llms.txt")}',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


def llms_txt(request):
    """llms.txt — a machine-readable site guide for AI crawlers (llmstxt.org)."""
    def absolute(path):
        return request.build_absolute_uri(path)

    lines = [
        '# Конкурент-Б (ТОО «Конкурент-Б»)',
        '',
        '> Казахстанская компания полного цикла железнодорожного строительства: '
        'проектирование, строительство, реконструкция, ремонт железных дорог и текущее '
        'содержание железнодорожных путей и прирельсовой инфраструктуры для промышленных '
        'предприятий, портов и логистических терминалов Казахстана.',
        '',
        'Работы выполняются квалифицированным персоналом из постоянного штата. '
        'Языки сайта: русский (/ru/) и английский (/en/).',
        '',
        '## Основные разделы',
        '',
        f'- [Главная]({absolute("/ru/")}): обзор компании и услуг',
        f'- [Услуги]({absolute("/ru/uslugi/")}): проектирование, строительство, реконструкция, технадзор, консалтинг',
        f'- [Проекты]({absolute("/ru/proekty/")}): портфолио выполненных объектов с параметрами',
        f'- [Техника]({absolute("/ru/tekhnika/")}): собственный парк путевой техники',
        f'- [О компании]({absolute("/ru/o-kompanii/")}): история, команда, руководство',
        f'- [FAQ]({absolute("/ru/faq/")}): ответы на частые вопросы о строительстве путей, сроках и стоимости',
        f'- [Контакты]({absolute("/ru/kontakty/")}): форма заявки и контактные данные',
        '',
        '## Инвесторам',
        '',
        f'- [Выбор площадки под строительство объекта]({absolute("/ru/investoram/vybor-ploshchadki/")})',
        f'- [Справочник терминов]({absolute("/ru/investoram/spravochnik-terminov/")})',
        f'- [Технология строительства]({absolute("/ru/investoram/tekhnologiya-stroitelstva/")})',
        f'- [ТЭО проекта строительства подъездного жд-пути]({absolute("/ru/investoram/teo-proekta/")})',
        f'- [Этапы строительства жд-пути]({absolute("/ru/investoram/etapy-stroitelstva/")})',
        '',
        '## Публикации',
        '',
        f'- [Новости]({absolute("/ru/novosti/")}): новости компании и завершённые проекты',
        f'- [Техническая информация]({absolute("/ru/tekhnicheskaya-informatsiya/")}): статьи о строительстве и нормативной базе',
        f'- [Книга директора]({absolute("/ru/direktoru-kniga/")}): аналитические материалы руководства',
        '',
        '## Служебные',
        '',
        f'- [Sitemap]({absolute("/sitemap.xml")})',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')
