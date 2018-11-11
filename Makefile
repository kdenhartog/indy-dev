target:
	./scripts/dependency_check.sh

build:
	./scripts/build.sh

start:
	./scripts/start.sh $(DIR)

stop:
	./scripts/stop.sh

cleanup:
	./scripts/cleanup.sh

refresh:
	./scripts/refresh.sh

