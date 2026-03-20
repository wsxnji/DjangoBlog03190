from django.db import migrations

def add_categories(apps, schema_editor):
    Category = apps.get_model('blog', 'Category')
    
    # 创建一级类目
    frontend, _ = Category.objects.get_or_create(
        name='前端',
        defaults={'index': 10}
    )
    backend, _ = Category.objects.get_or_create(
        name='后端',
        defaults={'index': 9}
    )
    algorithm, _ = Category.objects.get_or_create(
        name='数据结构与算法',
        defaults={'index': 8}
    )
    ops, _ = Category.objects.get_or_create(
        name='运维',
        defaults={'index': 7}
    )
    ai, _ = Category.objects.get_or_create(
        name='人工智能',
        defaults={'index': 6}
    )
    
    # 前端类目下的二级类目
    frontend_subcategories = ['HTML', 'JS', 'CSS', 'vue', 'NodeJS']
    for name in frontend_subcategories:
        Category.objects.get_or_create(
            name=name,
            parent_category=frontend,
            defaults={'index': 0}
        )
    
    # 后端类目下的二级类目
    backend_subcategories = ['Java', 'Go', 'PHP']
    for name in backend_subcategories:
        Category.objects.get_or_create(
            name=name,
            parent_category=backend,
            defaults={'index': 0}
        )
    
    # 修改Python技术为Python，并移到后端类目下
    try:
        python_category = Category.objects.get(name='Python技术')
        python_category.name = 'Python'
        python_category.parent_category = backend
        python_category.save()
    except Category.DoesNotExist:
        # 如果不存在则创建
        Category.objects.get_or_create(
            name='Python',
            parent_category=backend,
            defaults={'index': 0}
        )

class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_blogsettings_color_scheme'),
    ]

    operations = [
        migrations.RunPython(add_categories),
    ]
