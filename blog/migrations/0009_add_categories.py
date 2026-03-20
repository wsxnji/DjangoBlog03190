from django.db import migrations


def add_categories(apps, schema_editor):
    Category = apps.get_model('blog', 'Category')
    
    protected_categories = ['前端', '后端', '数据结构与算法', '运维', '人工智能']
    
    frontend, _ = Category.objects.get_or_create(
        name='前端',
        defaults={'parent_category': None, 'index': 100}
    )
    
    backend, _ = Category.objects.get_or_create(
        name='后端',
        defaults={'parent_category': None, 'index': 99}
    )
    
    algo, _ = Category.objects.get_or_create(
        name='数据结构与算法',
        defaults={'parent_category': None, 'index': 98}
    )
    
    ops, _ = Category.objects.get_or_create(
        name='运维',
        defaults={'parent_category': None, 'index': 97}
    )
    
    ai, _ = Category.objects.get_or_create(
        name='人工智能',
        defaults={'parent_category': None, 'index': 96}
    )
    
    frontend_subs = ['HTML', 'JS', 'CSS', 'vue', 'NodeJS']
    for idx, name in enumerate(frontend_subs):
        Category.objects.get_or_create(
            name=name,
            defaults={'parent_category': frontend, 'index': 50 - idx}
        )
    
    backend_subs = ['Java', 'Go', 'PHP']
    for idx, name in enumerate(backend_subs):
        Category.objects.get_or_create(
            name=name,
            defaults={'parent_category': backend, 'index': 50 - idx}
        )
    
    try:
        python_cat = Category.objects.get(name='Python技术')
        python_cat.name = 'Python'
        python_cat.parent_category = backend
        python_cat.save()
    except Category.DoesNotExist:
        pass


def reverse_add_categories(apps, schema_editor):
    Category = apps.get_model('blog', 'Category')
    
    Category.objects.filter(name__in=['HTML', 'JS', 'CSS', 'vue', 'NodeJS']).delete()
    Category.objects.filter(name__in=['Java', 'Go', 'PHP']).delete()
    Category.objects.filter(name__in=['前端', '后端', '数据结构与算法', '运维', '人工智能']).delete()
    
    try:
        python_cat = Category.objects.get(name='Python')
        python_cat.name = 'Python技术'
        python_cat.parent_category = None
        python_cat.save()
    except Category.DoesNotExist:
        pass


class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0008_blogsettings_color_scheme'),
    ]

    operations = [
        migrations.RunPython(add_categories, reverse_add_categories),
    ]
