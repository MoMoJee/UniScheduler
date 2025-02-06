from django.db import models
from django.contrib.auth.models import User
import json
# 这里定义用户信息类

'''
定义一个 UserProfile 模型来存储用户额外信息是一种非常常见且推荐的方式。
Django 默认的用户模型（django.contrib.auth.models.User）已经提供了基本的用户信息字段，如用户名、密码、邮箱等。
然而，在实际应用中，我们通常需要存储更多用户相关的额外信息，例如电话号码、地址、头像等。通过扩展默认的用户模型，可以方便地实现这一需求。
'''
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_joined = User.date_joined
    # phone_number = models.CharField(max_length=15, blank=True)
    # address = models.TextField(blank=True)
    # avatar = models.ImageField(upload_to='avatars/', blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
# UserProfile 模型通常用于存储与用户相关的额外信息。
# Django 的默认 User 模型已经包含了基本的用户信息（如用户名、密码、邮箱等），
# 但有时你可能需要存储更多用户相关的数据，比如电话号码、地址、头像等。
#一对一关系：通过 OneToOneField 将 UserProfile 与 User 模型关联起来，确保每个用户只有一个对应的 UserProfile。
# 便于管理：可以在 Django Admin 中方便地管理用户及其额外信息。



class UserData(models.Model):
    # 这里定义用户数据模型，
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=100)
    value = models.TextField()
    # 使用 TextField 存储序列化后的数据。python自带的SQLite不支持JSON格式，因此下面有一套解析函数

    def __str__(self):
        return f"{self.user.username} - {self.key}"

    def set_value(self, data):
        self.value = json.dumps(data)

    def get_value(self):
        if not self.value:  # 如果 value 是空的，返回空字典
            return {}
        try:
            return json.loads(self.value)
        except json.JSONDecodeError as e:
            # 如果反序列化失败，记录错误并返回空字典
            print(f"JSONDecodeError: {e}")
            return {}
    # 于是，我们创建了用户模型，通过字符串的key+JSON格式的value存储，其中value如果是非文本类型，是需要额外解析的。为了统一，这里推荐全部解析使用。


# UserData 模型通常用于存储用户动态生成的数据，这些数据可能因用户而异，且可能需要频繁更新或扩展。例如，用户在某个应用中生成的配置数据、记录的数据等
# 动态数据存储：存储用户生成的动态数据，这些数据可能因用户而异，且可能需要频繁更新。
# 多对一关系：通过 ForeignKey 将 UserData 与 User 模型关联起来，允许每个用户有多个数据记录。
# 灵活扩展：可以通过添加新的 key 来扩展数据结构，而无需修改数据库表结构。