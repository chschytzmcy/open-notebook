.PHONY: build clean install test uninstall

build:
	@echo "Building opennotebook CLI..."
	cd .. && .venv/bin/python -m PyInstaller cli/opennotebook.spec --noconfirm --distpath dist
	@echo "Build complete: dist/opennotebook/"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf ../dist/opennotebook
	rm -rf ../build
	find .. -name "*.spec" -delete 2>/dev/null || true
	@echo "Clean complete"

install:
	@echo "Installing to ~/.local/bin/..."
	@if [ ! -d "../dist/opennotebook" ]; then \
		echo "Binary not found, building first..."; \
		make build; \
	fi
	mkdir -p ~/.local/bin
	rm -rf ~/.local/bin/opennotebook-dir
	rm -f ~/.local/bin/opennotebook
	cp -rf ../dist/opennotebook ~/.local/bin/opennotebook-dir
	ln -sf ~/.local/bin/opennotebook-dir/opennotebook ~/.local/bin/opennotebook
	chmod +x ~/.local/bin/opennotebook
	@echo "Installed: opennotebook"

uninstall:
	@echo "Uninstalling opennotebook..."
	rm -rf ~/.local/bin/opennotebook-dir
	rm -f ~/.local/bin/opennotebook
	@echo "Uninstalled"

test:
	@echo "Testing CLI..."
	../dist/opennotebook/opennotebook --help

.DEFAULT_GOAL := build