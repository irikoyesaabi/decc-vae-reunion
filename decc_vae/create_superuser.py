"""Crée le compte administrateur par défaut (admin / admin123)."""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "decc_vae.settings")

import django

django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = "admin"
password = "admin123"
email = "admin@decc-vae.ne"

user, created = User.objects.get_or_create(
    username=username,
    defaults={"email": email, "is_staff": True, "is_superuser": True},
)
user.is_staff = True
user.is_superuser = True
user.set_password(password)
user.save()
print("Superutilisateur admin prêt (mot de passe : admin123)." if created else "Compte admin mis à jour.")
