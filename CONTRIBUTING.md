# Contributing to Padel Watcher

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Set up development environment (see DEVELOPMENT.md)

## Development Workflow

1. **Make your changes** in your feature branch
2. **Write tests** for your changes
3. **Run tests** to ensure nothing broke
4. **Update documentation** if needed
5. **Commit your changes** with clear messages
6. **Push to your fork**
7. **Create a Pull Request**

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Use type hints where appropriate

## Commit Messages

Write clear, descriptive commit messages:

```
Add feature: Brief description

Longer explanation of what changed and why.
- Detail 1
- Detail 2
```

Examples:
- `Add: Indoor/outdoor court filtering`
- `Fix: Search order time range validation`
- `Update: API documentation for new endpoint`
- `Refactor: Extract common service methods`

## Pull Request Process

1. **Update documentation** for any API changes
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update README.md** if needed
5. **Request review** from maintainers

### PR Checklist

- [ ] Code follows project style
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

## Testing

Always test your changes:

```bash
cd backend
python tests/test_api.py
python tests/test_comprehensive_time_range.py
```

## Areas for Contribution

### High Priority
- Web frontend implementation
- Email/SMS notification service
- PostgreSQL database support
- Rate limiting implementation
- User management improvements

### Medium Priority
- Additional court providers
- Advanced filtering options
- Caching layer
- API documentation improvements
- Performance optimizations

### Low Priority
- Mobile app
- Court booking integration
- Analytics dashboard
- Advanced scheduling options

## Questions?

- Check existing issues
- Read the documentation
- Ask in discussions
- Create a new issue for bugs

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
