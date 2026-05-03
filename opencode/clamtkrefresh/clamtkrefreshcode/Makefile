# Makefile for ClamTK Refresh

.PHONY: all build install clean uninstall test

# Variables
PREFIX ?= /usr/local
BINDIR = $(PREFIX)/bin
PERL5DIR = /usr/share/perl5
CLAMTK_DIR = $(PERL5DIR)/ClamTk
ICONDIR = /usr/share/icons/hicolor/256x256/apps
APPDIR = /usr/share/applications

# Build
build:
	@echo "Building clamtkrefresh..."
	@mkdir -p build$(BINDIR) build$(CLAMTK_DIR) build$(APPDIR) build$(ICONDIR)
	@cp bin/clamtkrefresh build$(BINDIR)/
	@chmod +x build$(BINDIR)/clamtkrefresh
	@cp lib/ClamTk/*.pm build$(CLAMTK_DIR)/
	@if [ -f ../clamtk-master/clamtk.desktop ]; then \
		sed 's/clamtk/clamtkrefresh/g; s/ClamTk/ClamTk Refresh/g' ../clamtk-master/clamtk.desktop > build$(APPDIR)/clamtkrefresh.desktop; \
	fi
	@cp images/clamtk.png build$(ICONDIR)/clamtkrefresh.png
	@echo "Build complete. Files are in the 'build' directory."

# Install
install: build
	@echo "Installing clamtkrefresh..."
	@sudo cp -r build/* /
	@echo "Installation complete. Run 'clamtkrefresh' to start."

# Uninstall
uninstall:
	@echo "Uninstalling clamtkrefresh..."
	@sudo rm -f $(BINDIR)/clamtkrefresh
	@sudo rm -rf $(CLAMTK_DIR)
	@sudo rm -f $(APPDIR)/clamtkrefresh.desktop
	@sudo rm -f $(ICONDIR)/clamtkrefresh.png
	@echo "Uninstallation complete."

# Clean
clean:
	@echo "Cleaning build files..."
	@rm -rf build/
	@echo "Clean complete."

# Test
test:
	@echo "Testing Perl syntax..."
	@perl -c bin/clamtkrefresh
	@for file in lib/ClamTk/*.pm; do \
		perl -c "$$file"; \
	done
	@echo "Syntax check passed!"

# Run (without installation)
run:
	@echo "Running clamtkrefresh..."
	@PERL5LIB=lib:$$PERL5LIB perl bin/clamtkrefresh

# Create tarball
dist:
	@echo "Creating distribution tarball..."
	@tar czf clamtkrefresh-$$(date +%Y%m%d).tar.gz --exclude build --exclude .git .
	@echo "Tarball created."

# Help
help:
	@echo "ClamTK Refresh - Available targets:"
	@echo "  build      - Build the project"
	@echo "  install    - Install system-wide"
	@echo "  uninstall  - Remove installed files"
	@echo "  clean      - Remove build files"
	@echo "  test       - Test Perl syntax"
	@echo "  run        - Run without installing"
	@echo "  dist       - Create distribution tarball"
	@echo "  help       - Show this help message"
