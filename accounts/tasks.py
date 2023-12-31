from celery import shared_task
from django.contrib.auth.mixins import UserPassesTestMixin
from kavenegar import *

@shared_task
def send_otp_code(phone_number, code):
	try:
		api = KavenegarAPI('place your kavenegar api key here')
		params = {
			'sender': '',
			'receptor': phone_number,
			'message': f'{code} کد تایید شما '
		}
		response = api.sms_send(params)
		print(response)
	except APIException as e:
		print(e)
	except HTTPException as e:
		print(e)


