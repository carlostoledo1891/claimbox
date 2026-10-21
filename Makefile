PY ?= python3
CERT_MACHINE ?= $(HOME)/Projects/cert-machine
export CERT_MACHINE

test:
	@$(PY) tests/battery.py $(if $(WRITE),--write,) | tail -40

lift:
	@$(PY) tools/lift.py

drift:
	@$(PY) tools/lift.py --check && $(PY) tools/platform.py --check

platform:
	@$(PY) tools/platform.py

.PHONY: test lift drift platform
