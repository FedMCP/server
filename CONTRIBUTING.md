# Contributing to FedMCP

Thank you for your interest in contributing to FedMCP! This document provides guidelines for contributing to the project.

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## 🚀 Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature or fix
4. Make your changes
5. Push to your fork and submit a pull request

## 💻 Development Setup

### Prerequisites
- Go 1.21+ for CLI and Go libraries
- Python 3.8+ for Python libraries and server
- Node.js 18+ for TypeScript libraries and UI
- Docker for running tests and local development

### Setting Up Your Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/fedmcp.git
cd fedmcp

# Python setup
cd core/python
pip install -e ".[dev]"

# Go setup
cd core/go
go mod download

# TypeScript setup
cd core/typescript
npm install

# Server setup
cd server
pip install -r requirements.txt
```

## 📝 Pull Request Process

1. **Before submitting**:
   - Ensure all tests pass
   - Update documentation as needed
   - Add tests for new functionality
   - Follow the coding standards

2. **PR Guidelines**:
   - Use a clear, descriptive title
   - Reference any related issues
   - Include a description of changes
   - Keep PRs focused and small

3. **Review Process**:
   - All PRs require at least one review
   - Address review feedback promptly
   - Maintain a respectful dialogue

## 🧪 Testing

### Running Tests

```bash
# Python tests
cd core/python && pytest

# Go tests  
cd core/go && go test ./...

# TypeScript tests
cd core/typescript && npm test

# Integration tests
cd tests && ./run_integration_tests.sh
```

### Writing Tests
- Write unit tests for all new functions
- Include integration tests for new features
- Aim for >80% code coverage
- Test edge cases and error conditions

## 🎨 Coding Standards

### Python
- Follow PEP 8
- Use type hints
- Format with `black`
- Lint with `flake8`

### Go
- Follow standard Go conventions
- Use `gofmt` and `golint`
- Handle all errors explicitly
- Write idiomatic Go code

### TypeScript
- Use TypeScript strict mode
- Follow ESLint rules
- Prefer functional programming patterns
- Document public APIs with JSDoc

## 📚 Documentation

- Update README files when adding features
- Add inline documentation for complex logic
- Include examples for new functionality
- Keep documentation concise and clear

## 🏗️ Architecture Decisions

When proposing significant changes:
1. Open an issue for discussion first
2. Consider backward compatibility
3. Think about multi-language consistency
4. Evaluate security implications

## 🐛 Reporting Issues

When reporting bugs:
- Use the issue template
- Include reproduction steps
- Specify your environment
- Attach relevant logs or errors

## 💡 Feature Requests

For new features:
- Check existing issues first
- Explain the use case
- Consider implementation approach
- Be open to alternatives

## 🔒 Security

- Never commit secrets or credentials
- Review dependencies for vulnerabilities
- Follow secure coding practices
- Report security issues privately to security@fedmcp.dev

## 📦 Release Process

Releases follow semantic versioning:
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

## 🙏 Recognition

Contributors will be recognized in:
- The CONTRIBUTORS file
- Release notes
- Project documentation

## 💬 Getting Help

- GitHub Discussions for questions
- Issues for bugs and features
- Email: contributors@fedmcp.dev

Thank you for contributing to FedMCP!