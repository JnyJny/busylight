
TARGET=busylight


PYPROJECT= pyproject.toml

.PHONY: docs/busylight.1.md \
        docs/busyserve.1.md \
	docs \
        MAJOR MINOR PATCH \
        major minor patch \
        push publish\
        patch_release minor_release major_release \
        release clean

all:
	@echo "major_release - push and publish a major release"
	@echo "minor_release - push and publish a minor release"
	@echo "patch_release - push and publish a patch release"
	@echo "push          - pushes commits and tags to origin/master"
	@echo "publish       - publish package to PyPI"
	@echo "report        - generate a code coverage report"
	@echo "mypy          - type check the code base"

major: MAJOR update

minor: MINOR update

patch: PATCH update

MAJOR:
	@poetry version major

MINOR:
	@poetry version minor

PATCH:
	@poetry version patch


docs: docs/busylight.1.md docs/busyserve.1.md

docs/busylight.1.md:
	@typer $(TARGET).__main__ utils docs --name busylight --output $@
	@sed -i '' -e  "s///g" $@

docs/busyserve.1.md:
	@typer --app webapi $(TARGET).__main__ utils docs --name busyserve --output $@
	@sed -i '' -e  "s///g" $@


update:
	@git add $(PYPROJECT)
	@awk '/^version =/ {print $$3}' $(PYPROJECT) | xargs git commit -m
	@awk '/^version =/{print $$3}' $(PYPROJECT) | xargs git tag

push:
	@git push --tags origin master

publish:
	@poetry build
	@poetry publish

requirements.txt: poetry.lock
	@poetry export -o $@
	@git add $@
	@git commit -m "export requirements from poetry for dependabot"

major_release: major push publish

minor_release: minor push publish

patch_release: patch push publish

release: patch_release

report:
	pytest --cov=./busylight --cov-report=html
	open htmlcov/index.html

mypy: MYPY= mypy
mypy:
	$(MYPY) --config-file $(PYPROJECT) $(TARGET)

clean:
	@rm -rf dist $(TARGET).egg-info *.log htmlcov

