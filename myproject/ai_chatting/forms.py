from django import forms
# 导入 Django 的 forms 模块，用于创建表单类。

class InputForm(forms.Form):
    # 定义一个名为 InputForm 的表单类，继承自 forms.Form。forms.Form 是 Django 提供的用于创建表单的基类。
    user_input = forms.CharField(label='Enter something', max_length=100)
    # 定义一个表单字段 user_input，字段类型为 CharField，表示用户输入的文本。
    # label='Enter something'：设置表单字段的标签，显示在表单中。
    # max_length=100：限制用户输入的最大长度为 100 个字符。
