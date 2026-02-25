from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        new_group, created = Group.objects.get_or_create(name='Managers')

        permissions_list = [
            'view_all_messages',
            'view_all_clients',
            'can_view_any_mailing',
            'can_disable_mailing',
            'view_user',
            'can_block_user',
        ]

        for perm in permissions_list:
            try:
                permission = Permission.objects.get(codename=perm)
                new_group.permissions.add(permission)
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Право {perm} не найдено. Проверь миграции!'))

        self.stdout.write(self.style.SUCCESS('Группа Managers создана и права назначены!'))
