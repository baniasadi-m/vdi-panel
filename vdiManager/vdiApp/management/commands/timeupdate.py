from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from ...models import VDIInfo
from sys import exit


class Command(BaseCommand):
    help = "update latest timestamp"

    def handle(self, *args, **options):
        try:
            vdi_info = VDIInfo.objects.all()
        except Exception as e:
            print(f"Database fetch data error: {e}")
            exit(3)
        if int(vdi_info.count()) != 1:
            exit(1)
        else:
            try:
                info  = vdi_info.first()
                info.latest_check = timezone.now()
                info.save(update_fields =['latest_check'])
            except Exception as e:
                print(f"Database update error: {e}")
                exit(2)
