mig:
	python3 manage.py makemigrations
	python3 manage.py migrate

run:
	 python manage.py runserver 0.0.0.0:8000

user:
	python3 manage.py createsuperuser

loaddata:
	python manage.py loaddata users customers debts products purchases purchaseitems sales saleitems