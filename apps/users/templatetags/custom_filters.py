# apps/users/templatetags/custom_filters.py
from django import template

# 注册过滤器（必须创建register对象）
register = template.Library()

# 自定义add_class过滤器
@register.filter(name='add_class')
def add_class(field, css_class):
    """
    给Django表单字段添加CSS类名
    :param field: 表单字段对象（如form.username）
    :param css_class: 要添加的CSS类名（如"form-control"）
    :return: 添加了类名的表单字段
    """
    # 判断字段是否有attrs属性（表单字段均有该属性）
    if hasattr(field, 'as_widget'):
        # 给字段添加css类名
        return field.as_widget(attrs={"class": css_class})
    return field