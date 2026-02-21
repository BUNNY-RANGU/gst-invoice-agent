# GST Invoice Agent - Test Suite

## Running Tests

### Run all tests:
```bash
pytest
```

### Run specific test file:
```bash
pytest tests/agents/test_gst_calculator.py
```

### Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

### View coverage report:
Open `htmlcov/index.html` in browser

## Test Structure
```
tests/
├── agents/          # Unit tests for agents
│   └── test_gst_calculator.py
├── api/             # API integration tests
│   └── test_endpoints.py
└── README.md        # This file
```

## Writing Tests

- Use descriptive test names
- Test both success and failure cases
- Aim for >80% code coverage
- Keep tests independent

## Test Coverage Goals

- Agents: >90%
- API Endpoints: >85%
- Overall: >80%