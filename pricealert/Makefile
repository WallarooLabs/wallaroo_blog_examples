celery-run:
	WITH_WALLAROO=False celery -A pricealert worker -B -l info

gdax-celery:
	python gdax_celery.py

gdax-wallaroo:
	python gdax_wallaroo.py

django-wallaroo-runserver:
	WITH_WALLAROO=True python manage.py runserver

django-celery-runserver:
	WITH_WALLAROO=False python manage.py runserver

gdax-wallaroo-receiver:
	python gdax_wallaroo_receiver.py
