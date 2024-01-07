from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(username, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ADMIN = 'admin'
    USER = 'user'
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (USER, 'User'),
    ]

    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=USER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name="user_set_custom",  # Custom related_name
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name="user_set_custom",  # Custom related_name
        help_text='Specific permissions for this user.',
    )

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.firstname} {self.lastname}"

    def get_short_name(self):
        return self.firstname

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'


class NewsItem(models.Model):
    title_en = models.CharField(max_length=200)
    title_ru = models.CharField(max_length=200)

    link = models.URLField()

    description_en = models.TextField()
    description_ru = models.TextField()

    category_en = models.CharField(max_length=100)
    category_ru = models.CharField(max_length=100)

    pub_date = models.DateTimeField()


class Comment(models.Model):
    news_item = models.ForeignKey(NewsItem, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.news_item.title_en}"


class LastFetch(models.Model):
    last_fetched = models.DateTimeField(default=timezone.now)



class LogEntry(models.Model):
    ATTACK_TYPES = [
        ('PS', 'Port Scan'),
        ('ID', 'Information Disclosure'),
        ('RCE', 'Remote Code Execution'),
        ('OTH', 'Other')
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255, null=True)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(null=True)
    absolute_uri = models.URLField(null=True)
    http_method = models.CharField(max_length=10, null=True)
    input = models.CharField(max_length=255, null=True)

    attackType = models.CharField(max_length=3, choices=ATTACK_TYPES, blank=True, null=True)

    def __str__(self):
        return f"{self.created_at} - {self.user} - {self.action}"


