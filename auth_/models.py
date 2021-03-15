import os
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, User, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from mirage import fields
from utils.utils import merge_dicts, get_avatar_profile_link


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    email = fields.EncryptedEmailField(blank=True, unique=True)
    username = fields.EncryptedCharField(
        max_length=150,
        unique=True,
        help_text=('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': ("Пользователь с таким логином уже существует."),
        },
    )
    is_active = models.BooleanField(default=True)
    first_name = models.CharField(('first name'), max_length=150, blank=True)
    last_name = models.CharField(('last name'), max_length=150, blank=True)
    date_joined = models.DateTimeField(('date joined'), default=timezone.now)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []
    is_staff = models.BooleanField(default=False,)

    objects = UserManager()

    class Meta:
        verbose_name = ('user')
        verbose_name_plural = ('Пользователи')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Profile(models.Model):
    user = models.OneToOneField("auth_.CustomUser", null=False, on_delete=models.CASCADE, verbose_name='Пользователь')
    first_name = fields.EncryptedCharField(default='', verbose_name='Имя')
    surname = fields.EncryptedCharField(default='', verbose_name='Фамилия')
    patronymic = fields.EncryptedCharField(default='', verbose_name='Отчество')
    partner = models.OneToOneField("utils.Partner", null=True, on_delete=models.CASCADE, related_name='+')
    avatar = models.ImageField(upload_to='avatars', blank=True, default='avatars/default.jpg')
    activated = models.BooleanField(default=False)
    whatsapp = fields.EncryptedCharField(default=None, null=True)
    instagram = fields.EncryptedCharField(default=None, null=True)
    telegram = fields.EncryptedCharField(default=None, null=True)



    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = ('Профили пользователей')

    def get_partner_list(self):
        return Profile.objects.filter(inviter=self).all()


    def upload_file(self, image_pillow):
        path = os.path.join(settings.MEDIA_ROOT, 'avatars', self.user.username + '.png')
        image_pillow.save(path)
        self.avatar = os.path.join('avatars', self.user.username + '.png')
        self.save()
        return get_avatar_profile_link(self)







