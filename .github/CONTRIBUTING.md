# Contributing to API-SCADA-TML

## Getting Started

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

## Development

### Environment Variables

Create a `.env` file with:
```
TML_SQL_SERVER=127.0.0.1,1433
TML_SQL_USER=tml_reader
TML_SQL_PASSWORD=your_password
TML_SQL_DATABASES=ProjectOWEN
TML_API_PORT=8787
```

### Running the API

```bash
python app.py
```

API will be available at `http://localhost:8787`

## Code Standards

- Follow PEP 8
- Use type hints where possible
- Write docstrings for all functions
- Include tests for new features

## Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/description`
3. Make your changes
4. Test your changes
5. Commit with clear messages
6. Push to your fork
7. Create a Pull Request

## Reporting Issues

Include:
- Clear description
- Steps to reproduce
- Expected behavior
- Actual behavior
- Python version and OS
