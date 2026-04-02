runserver:
	DJANGO_ENV=dev python manage.py runserver

init_tasks:
	DJANGO_ENV=dev python manage.py init_tasks

runscheduler:
	DJANGO_ENV=dev python manage.py runscheduler

runworker:
	DJANGO_ENV=dev python manage.py runworker

runrqworker:
	DJANGO_ENV=dev python manage.py rqworker default email maintenance

apidoc:
	python manage.py spectacular --file openapi.yaml