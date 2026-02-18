PYTHON ?= python3

.PHONY: install test help

help:
	@echo "Targets disponibles:"
	@echo "  make install        # Installe l'outil dans .venv-facade2d"
	@echo "  make test           # Lance les tests unitaires"
	@echo "  make process ARGS=\"--input ./photo.jpg --output ./out\""
	@echo "  make api            # Démarre l'API REST locale"

install:
	bash scripts/install_facade2d.sh

test:
	$(PYTHON) -m unittest -v tests/test_pipeline_synthetic.py

process:
	@if [ -z "$(ARGS)" ]; then \
		echo "Usage: make process ARGS=\"--input ./photo.jpg --output ./out\""; \
		exit 1; \
	fi
	bash scripts/facade2d_process.sh $(ARGS)

api:
	bash scripts/facade2d_api.sh
