from django.utils import timezone
from django.core.management.base import BaseCommand
from ...models import VDIInfo
from sys import exit
from django.conf import settings


class Command(BaseCommand):
    help = "create license info"

    def add_arguments(self, parser):
        parser.add_argument('-d','--days', type=int, help="Number of months from creation until expiration date")
        parser.add_argument('-p','--profiles', type=int, help="Number of profiles permitted")
        parser.add_argument('-a','--api', type=int, help="Enable/Disable Api")
        parser.add_argument('-N','--name', type=str, help="Full organization name")
        parser.add_argument('-n','--sname', type=str, help="Short name of organization")


    def handle(self, *args, **options):
        expire_date = timezone.now() + timezone.timedelta(options['days'])
        input_data = {}
        input_data.update({
            'company_short_name': options['sname'],
            'company_name' : options['name'],
            'limit_user' : options['profiles'],
            'expired_at' : expire_date
        })
        if int(options['api']) == 1:
            input_data.update({
                'api_enabled': True
            })
        else:
            input_data.update({
                'api_enabled': False
            }) 
        try:
            vdi_info = VDIInfo.objects.create(**input_data)
            if vdi_info.pk is None:
                print("Cannot register license info maybe had a license")
            else:
                print("License registered successfully")
        except Exception as e:
            print(f"Database create error: {e}")
            exit(1)

