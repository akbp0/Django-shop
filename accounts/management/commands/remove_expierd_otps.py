from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from accounts.models import OtpModel


class Command(BaseCommand):
    help = 'for delete expierd otps'

    def handle(self, *args, **options):
        expired_time = datetime.now()-timedelta(minutes=2)
        otps = OtpModel.objects.filter(created__lt=expired_time)
        count =  otps.count()
        otps.delete()
        self.stdout.write(f'{count} codes successfully deleted')
