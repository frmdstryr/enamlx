docs:
	cd docs
	make html
isort:
	isort enamlx examples
typecheck:
	mypy enamlx examples --ignore-missing-imports
lintcheck:
	flake8 --ignore=E501 enamlx examples
reformat:
	black enamlx examples
test:
	pytest -v tests --cov enamlx --cov-report xml --asyncio-mode auto

precommit: isort reformat lintcheck
