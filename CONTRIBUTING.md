# Contributing to BioDockify MD Universal

Thank you for your interest in contributing!

## Development Setup

```bash
# Clone repository
git clone https://github.com/tajo9128/MD-lite.git
cd MD-lite

# Create virtual environment
python -m venv venv

# Install dependencies
pip install -r requirements.txt
```

## Coding Standards

- Follow PEP 8 style guide
- Use type hints where possible
- Add docstrings to new functions and classes
- Keep functions focused and modular

## Testing

Before submitting a pull request, test your changes:

```bash
# Test imports
python -c "from main import main"

# Test GPU detection
python main.py --detect-gpu
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Reporting Issues

Please open an issue on GitHub with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior

---

*This project follows the Contributor Covenant Code of Conduct.*
