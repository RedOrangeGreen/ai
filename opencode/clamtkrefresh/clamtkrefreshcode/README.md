# ClamTK Refresh

A modern GUI redesign of ClamTk, the popular ClamAV front-end for Linux systems.

![ClamTK Refresh](images/clamtk_300x300.png)

## 🎨 Modern Design

ClamTK Refresh transforms the original ClamTk interface with a contemporary, card-based design inspired by modern UI principles. Built on the solid foundation of ClamTk by Dave M, this refresh brings a clean, intuitive interface to virus scanning on Linux.

## ✨ Features

- **Modern Card-Based Layout** - Clean, organized interface with visual sections
- **Enhanced Visual Design** - Custom CSS styling with modern color scheme
- **Optimized for Productivity** - All 11 action cards visible without scrolling
- **Larger Window** - 1100x800 pixels to display all options
- **Compact Cards** - 150x110px cards with 36px icons
- **Section Organization** - Scan, Protection, and Settings sections
- **Hover Effects** - Interactive elements with visual feedback

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [Building](#-building)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Installation

### Quick Run (No Installation Required)

```bash
git clone https://github.com/yourusername/clamtkrefresh.git
cd clamtkrefresh
./bin/clamtkrefresh
```

### System-Wide Installation

```bash
git clone https://github.com/yourusername/clamtkrefresh.git
cd clamtkrefresh
./build.sh
sudo cp -r build/* /
```

After installation, you can run directly:
```bash
clamtkrefresh
```

### Requirements

- Perl 5
- Gtk3 Perl module (`sudo apt install libgtk3-perl` on Debian/Ubuntu)
- ClamAV (`sudo apt install clamav clamav-daemon`)

## 💻 Usage

### Graphical Interface

Simply run the executable:
```bash
./bin/clamtkrefresh
```

### Command-Line Scanning

```bash
./bin/clamtkrefresh /path/to/file
./bin/clamtkrefresh /path/to/directory
```

### Right-Click Scanning

For file manager integration, install the appropriate plugin:
- **GNOME (Nautilus)**: clamtk-gnome
- **KDE (Dolphin)**: clamtk-kde
- **XFCE (Thunar)**: thunar-sendto-clamtk
- **MATE (Nemo)**: nemo-sendto-clamtk

## 🔧 Building

Use the provided build script to create a distributable package:

```bash
cd clamtkrefresh
./build.sh
```

This will:
- Create the `build/` directory structure
- Copy the executable to `build/usr/local/bin/`
- Copy Perl modules to `build/usr/share/perl5/ClamTk/`
- Prepare desktop file and icon

### Manual Build

```bash
mkdir -p build/usr/local/bin build/usr/share/perl5/ClamTk
cp bin/clamtkrefresh build/usr/local/bin/
chmod +x build/usr/local/bin/clamtkrefresh
cp lib/ClamTk/*.pm build/usr/share/perl5/ClamTk/
```

## 📊 GUI Comparison

### Original ClamTk
- Icon views with small 24px icons
- Window size: 340x400 (requires scrolling)
- Vertical stacking of all elements
- Basic separators between sections

### ClamTK Refresh
- Card-based layout with 36px icons
- Window size: 1100x800 (no scrolling needed)
- Organized sections: Scan, Protection, Settings
- Modern CSS styling with `#007aff` accent color
- Hero section with title and subtitle

## 📁 Project Structure

```
clamtkrefresh/
├── bin/
│   └── clamtkrefresh          # Main executable
├── lib/
│   └── ClamTk/
│       ├── GUI.pm             # Modern GUI implementation
│       ├── Analysis.pm
│       ├── App.pm
│       └── ... (other modules)
├── images/
│   ├── clamtk.png
│   ├── clamtk.xpm
│   └── clamtk_300x300.png
├── doc/
│   ├── clamtkrefresh.html     # Detailed documentation
│   └── SUMMARY.txt
├── build/                     # Build output directory
├── build.sh                   # Build script
├── README.md
├── LICENSE
└── CHANGES
```

## 🎨 Design Details

### Color Scheme
- **Background**: `#f5f5f7`
- **Cards**: `#ffffff`
- **Accent**: `#007aff`
- **Text Primary**: `#1d1d1f`
- **Text Secondary**: `#86868b`
- **Border**: `#d2d2d7`

### Window Layout
- **Size**: 1100x800 pixels
- **Hero Section**: 80px height
- **Cards**: 150x110 pixels
- **Icons**: 36 pixels
- **Grid Spacing**: 8px
- **Section Spacing**: 6-12px

## 📦 Distribution

### Creating a Tarball

```bash
tar czf clamtkrefresh-v1.0.tar.gz clamtkrefresh/
```

### Debian/Ubuntu Package

Use the provided build structure to create a .deb package:

```bash
cd clamtkrefresh
./build.sh
# Use dpkg-deb or similar tools with the build/ directory
```

## 🐛 Troubleshooting

### Perl Can't Find Modules

Ensure the `lib/` directory is in your Perl path:

```bash
export PERL5LIB=/path/to/clamtkrefresh/lib:$PERL5LIB
./bin/clamtkrefresh
```

### Missing Gtk3 Perl Module

Install it with:

```bash
# Debian/Ubuntu
sudo apt install libgtk3-perl

# Fedora
sudo dnf install perl-Gtk3

# CentOS/RHEL
sudo yum install perl-Gtk3
```

### ClamAV Not Found

Install ClamAV:

```bash
# Debian/Ubuntu
sudo apt install clamav clamav-daemon

# Fedora
sudo dnf install clamav clamav-update

# CentOS/RHEL
sudo yum install clamav clamav-update
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow the existing code style
- Test your changes thoroughly
- Update documentation as needed
- Keep the modern design principles in mind

## 📄 License

ClamTK Refresh is distributed under the same license as ClamTk:

- GNU General Public License (version 1 or later), OR
- The "Artistic License"

Copyright (C) 2004-2024 Dave M, Refresh Design 2026

## 🙏 Acknowledgments

- **Dave M** - Original ClamTk creator and maintainer (2004-2024)
- **ClamAV Team** - For the excellent antivirus engine
- **Gtk3-Perl Community** - For the Perl GTK3 bindings
- **Contributors** - Everyone who has contributed to ClamTk over the years

## 📞 Contact

- **Original ClamTk**: dave.nerd@gmail.com
- **Refresh Design**: [Your Contact Info]

## 🔗 Links

- [Original ClamTk Repository](https://github.com/dave-theunsub/clamtk)
- [ClamAV Official Site](https://www.clamav.net)
- [GTK3 Perl Documentation](https://developer.gnome.org/gtk3/stable/)

## 📝 Notes

- This is a UI redesign only - all scanning functionality comes from the original ClamTk
- The original ClamTk is no longer maintained (see [issue #163](https://github.com/dave-theunsub/clamtk/issues/163))
- ClamTK Refresh maintains compatibility with existing ClamTk plugins
- Version 7.xx design philosophy - modern, clean, intuitive

---

**ClamTK Refresh** - Modern antivirus scanning for Linux 🛡️
