from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

# Register your models here.
from .models import Article, Category, Tag, Links, SideBar, BlogSettings


class ArticleForm(forms.ModelForm):
    # body = forms.CharField(widget=AdminPagedownWidget())

    class Meta:
        model = Article
        fields = '__all__'


def makr_article_publish(modeladmin, request, queryset):
    queryset.update(status='p')


def draft_article(modeladmin, request, queryset):
    queryset.update(status='d')


def close_article_commentstatus(modeladmin, request, queryset):
    queryset.update(comment_status='c')


def open_article_commentstatus(modeladmin, request, queryset):
    queryset.update(comment_status='o')


makr_article_publish.short_description = _('Publish selected articles')
draft_article.short_description = _('Draft selected articles')
close_article_commentstatus.short_description = _('Close article comments')
open_article_commentstatus.short_description = _('Open article comments')


class ArticlelAdmin(admin.ModelAdmin):
    list_per_page = 20
    search_fields = ('body', 'title')
    form = ArticleForm
    list_display = (
        'id',
        'title',
        'author',
        'link_to_category',
        'creation_time',
        'views',
        'status',
        'type',
        'article_order')
    list_display_links = ('id', 'title')
    list_filter = ('status', 'type', 'category')
    date_hierarchy = 'creation_time'
    filter_horizontal = ('tags',)
    exclude = ('creation_time', 'last_modify_time')
    view_on_site = True
    actions = [
        makr_article_publish,
        draft_article,
        close_article_commentstatus,
        open_article_commentstatus]
    raw_id_fields = ('author', 'category',)

    def link_to_category(self, obj):
        info = (obj.category._meta.app_label, obj.category._meta.model_name)
        link = reverse('admin:%s_%s_change' % info, args=(obj.category.id,))
        return format_html(u'<a href="%s">%s</a>' % (link, obj.category.name))

    link_to_category.short_description = _('category')

    def get_form(self, request, obj=None, **kwargs):
        form = super(ArticlelAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['author'].queryset = get_user_model(
        ).objects.filter(is_superuser=True)
        return form

    def save_model(self, request, obj, form, change):
        super(ArticlelAdmin, self).save_model(request, obj, form, change)

    def get_view_on_site_url(self, obj=None):
        if obj:
            url = obj.get_full_url()
            return url
        else:
            from djangoblog.utils import get_current_site
            site = get_current_site().domain
            return site


class TagAdmin(admin.ModelAdmin):
    exclude = ('slug', 'last_mod_time', 'creation_time')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_category', 'index')
    exclude = ('slug', 'last_mod_time', 'creation_time')
    
    # 受保护的一级类目名称（只有超级管理员可修改）
    PROTECTED_CATEGORIES = ['前端', '后端', '数据结构与算法', '运维', '人工智能']
    
    def has_change_permission(self, request, obj=None):
        """
        检查用户是否有修改权限
        对于受保护的分类，只有超级管理员可以修改
        """
        # 如果是超级管理员，直接返回True
        if request.user.is_superuser:
            return True
            
        # 如果是修改已有对象
        if obj is not None:
            # 检查是否是受保护的分类（包括这些分类的子分类）
            if self._is_protected_category(obj):
                return False
        
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """
        检查用户是否有删除权限
        对于受保护的分类，只有超级管理员可以删除
        """
        if request.user.is_superuser:
            return True
            
        if obj is not None:
            if self._is_protected_category(obj):
                return False
                
        return super().has_delete_permission(request, obj)
    
    def _is_protected_category(self, category):
        """
        检查分类是否属于受保护的分类
        包括受保护的一级类目及其所有子分类
        """
        # 检查当前分类是否是受保护的一级类目
        if category.name in self.PROTECTED_CATEGORIES and category.parent_category is None:
            return True
        
        # 检查所有父级分类是否有受保护的
        current = category
        while current.parent_category is not None:
            current = current.parent_category
            if current.name in self.PROTECTED_CATEGORIES:
                return True
        
        return False
    
    def get_queryset(self, request):
        """
        获取查询集
        非超级管理员可以看到受保护的分类，但不能修改
        """
        return super().get_queryset(request)
    
    def save_model(self, request, obj, form, change):
        """
        保存模型时的额外检查
        防止非超级管理员修改受保护分类的名称或层级
        """
        if not request.user.is_superuser and change:
            # 获取原始对象
            original_obj = self.model.objects.get(pk=obj.pk)
            
            # 检查是否在修改受保护分类的关键属性
            if self._is_protected_category(original_obj):
                # 不允许修改名称、父分类和排序
                if (obj.name != original_obj.name or 
                    obj.parent_category != original_obj.parent_category):
                    from django.contrib import messages
                    messages.error(request, '您没有权限修改受保护的分类信息')
                    return  # 不保存修改
        
        super().save_model(request, obj, form, change)


class LinksAdmin(admin.ModelAdmin):
    exclude = ('last_mod_time', 'creation_time')


class SideBarAdmin(admin.ModelAdmin):
    list_display = ('name', 'content', 'is_enable', 'sequence')
    exclude = ('last_mod_time', 'creation_time')


class BlogSettingsAdmin(admin.ModelAdmin):
    """单例配置Admin - 直接跳转到编辑页面"""

    def has_add_permission(self, request):
        """如果已经存在配置，则禁止添加"""
        return not BlogSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """禁止删除配置"""
        return False

    def changelist_view(self, request, extra_context=None):
        """列表页直接跳转到编辑页面"""
        from django.http import HttpResponseRedirect
        obj = BlogSettings.objects.first()
        if obj:
            return HttpResponseRedirect(
                reverse('admin:blog_blogsettings_change', args=[obj.pk])
            )
        # 如果不存在配置，跳转到添加页面
        return HttpResponseRedirect(
            reverse('admin:blog_blogsettings_add')
        )

    def save_model(self, request, obj, form, change):
        """保存设置时清除缓存"""
        super().save_model(request, obj, form, change)
        # 确保缓存被清除
        from djangoblog.utils import cache
        cache.clear()
        self.message_user(request, '设置已保存，缓存已清除')
