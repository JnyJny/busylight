
TARGET=busylight

VERSION_FILE= $(TARGET)/__version__.py
PYPROJECT= pyproject.toml

.PHONY: $(VERSION_FILE) docs/busylight.1.md \
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

major: MAJOR update

minor: MINOR update

patch: PATCH update

MAJOR:
	@poetry version major

MINOR:
	@poetry version minor

PATCH:
	@poetry version patch


docs/busylight.1.md:
	@typer $(TARGET).__main__ utils docs --name busylight --output $@
	@sed -i '' -e  "s///g" $@


update: $(VERSION_FILE)
	@git add $(PYPROJECT) $(VERSION_FILE)
	@awk '{print $$3}' $(VERSION_FILE) | xargs git commit -m
	@awk '{print $$3}' $(VERSION_FILE) | xargs git tag

$(VERSION_FILE):
	@awk '/^version/ {print $$0}' $(PYPROJECT) | sed "s/version/__version__/" > $@

push:
	@git push --tags origin master

publish:
	@poetry build
	@poetry publish

patch_release: patch push publish

major_release: major push publish

minor_release: minor push publish

release: patch_release

clean:
	@rm -rf dist $(TARGET).egg-info *.log
