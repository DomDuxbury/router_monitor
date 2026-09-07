install:
	pip install -r requirements.txt
	pre-commit install

start:
	./run.sh

docker:
	docker-compose up
