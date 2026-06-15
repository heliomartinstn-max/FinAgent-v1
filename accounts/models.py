from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class NivelAcesso(models.Model):
    NIVEIS_CHOICES = (
        ('ADMIN', 'Administrador'),
        ('ANALISTA', 'Analista Financeiro'),
        ('GESTOR', 'Gestor/Diretoria'),
    )
    nome = models.CharField(max_length=50, choices=NIVEIS_CHOICES, unique=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.get_nome_display()

class User(AbstractUser):
    nome_completo = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    nivel_acesso = models.ForeignKey(NivelAcesso, on_delete=models.SET_NULL, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nome_completo']
    
    # Adicionando related_name para evitar conflitos com default User
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="custom_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_set",
        related_query_name="user",
    )

    def __str__(self):
        return self.email
