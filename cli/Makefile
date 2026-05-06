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
	@echo "Building opennotebook CLI..."
	make build
	@echo "Installing to ~/.local/bin/..."
	mkdir -p ~/.local/bin
	rm -rf ~/.local/bin/opennotebook-dir
	rm -f ~/.local/bin/opennotebook
	cp -rf ../dist/opennotebook ~/.local/bin/opennotebook-dir
	ln -sf ~/.local/bin/opennotebook-dir/opennotebook ~/.local/bin/opennotebook
	chmod +x ~/.local/bin/opennotebook
	@echo "Installed: opennotebook"

	@echo "Installing skills to ~/.agents/skills/..."
	@for skill in skills/*/; do \
		skill_name=$$(basename $$skill); \
		rm -rf ~/.agents/skills/$$skill_name; \
		cp -r $$skill ~/.agents/skills/; \
		echo "  Installed skill: $$skill_name"; \
	done
	@echo "Skills installed"

	@echo "Creating symlinks in ~/.claude/skills/..."
	@for skill in skills/*/; do \
		skill_name=$$(basename $$skill); \
		rm -f ~/.claude/skills/$$skill_name; \
		ln -sf ../../.agents/skills/$$skill_name ~/.claude/skills/$$skill_name; \
		echo "  Linked: $$skill_name"; \
	done
	@echo "Symlinks created"

uninstall:
	@echo "Uninstalling opennotebook..."
	rm -rf ~/.local/bin/opennotebook-dir
	rm -f ~/.local/bin/opennotebook
	@echo "Uninstalled"

	@echo "Removing symlinks from ~/.claude/skills/..."
	@for skill in skills/*/; do \
		skill_name=$$(basename $$skill); \
		rm -f ~/.claude/skills/$$skill_name; \
		echo "  Removed symlink: $$skill_name"; \
	done

	@echo "Uninstalling skills..."
	@for skill in skills/*/; do \
		skill_name=$$(basename $$skill); \
		rm -rf ~/.agents/skills/$$skill_name; \
		echo "  Removed skill: $$skill_name"; \
	done
	@echo "Skills uninstalled"

test:
	@echo "Running unit tests..."
	cd .. && .venv/bin/python -m pytest cli/tests/ -v

.DEFAULT_GOAL := build