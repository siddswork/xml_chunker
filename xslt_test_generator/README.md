# XSLT Test Generator

An AI-powered application that generates comprehensive Gherkin test cases for XSLT transformations by analyzing XSLT files and corresponding XSD schemas.

## Features

- 🤖 **AI-Powered Analysis**: Uses multiple LLM providers (OpenAI, Anthropic, Google) to analyze XSLT and XSD files
- 🧪 **Gherkin Test Generation**: Creates comprehensive BDD test scenarios with proper Given/When/Then structure
- 📊 **Coverage Analysis**: Provides detailed coverage reports for templates, conditions, and schema elements
- 🔄 **Multi-LLM Support**: Switch between different LLM providers via LiteLLM
- 📈 **Evaluation Ready**: Built-in evaluation framework using DeepEval
- 🎯 **CrewAI Agents**: Specialized agents for XSLT analysis, XSD analysis, and test case generation

## Installation

1. Clone the repository and navigate to the project directory:
```bash
cd xslt_test_generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Quick Start

Generate test cases for your XSLT transformation:

```bash
python -m src.main \
  /path/to/your/transform.xslt \
  /path/to/your/schema.xsd \
  /path/to/output/directory \
  --verbose
```

## Example Usage

Using the OrderCreate XSLT from our analysis:

```bash
python -m src.main \
  ../resource/orderCreate/xslt/OrderCreate_MapForce_Full.xslt \
  ../resource/orderCreate/input_xsd/AMA_ConnectivityLayerRQ.xsd \
  ./output \
  --provider openai \
  --verbose
```

## Output Files

The generator creates several output files:

- `{name}_tests.feature` - Main Gherkin test cases
- `{name}_analysis.md` - Detailed analysis report  
- `{name}_metadata.yaml` - Test generation metadata

## Configuration

Edit `config.yaml` to customize:

- LLM providers and models
- Agent behavior and settings
- Output formats
- Evaluation parameters

## Architecture

The application uses a multi-agent architecture:

### Agents
- **XSLT Analyzer Agent**: Analyzes transformation logic and patterns
- **XSD Schema Agent**: Analyzes input schema structure and constraints  
- **Test Case Generator Agent**: Creates comprehensive Gherkin scenarios

### Tools
- **LLM Client**: Multi-provider LLM interface using LiteLLM
- **File Manager**: File I/O operations with validation
- **XML Tools**: XSLT/XSD parsing and analysis utilities

## Development

### Project Structure
```
src/
├── agents/           # CrewAI agents
├── tools/           # Utility tools and LLM client
├── config/          # Configuration management
└── main.py          # CLI application entry point
```

### Adding New LLM Providers

1. Update `config.yaml` with new provider settings
2. Add API key to `.env`
3. LiteLLM handles the provider integration automatically

### Extending Analysis

To add new analysis capabilities:

1. Extend the appropriate analyzer class in `tools/xml_tools.py`
2. Update the corresponding agent to use new analysis
3. Modify the test case generator to incorporate new insights

## Evaluation

The application includes built-in evaluation using DeepEval:

```python
# Example evaluation (to be implemented)
from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric

metric = AnswerRelevancyMetric(threshold=0.8)
# Evaluate generated test cases
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Roadmap

### Phase 1: MVP (Current)
- ✅ Basic XSLT/XSD analysis
- ✅ Gherkin test case generation  
- ✅ Multi-LLM support
- ✅ CLI interface

### Phase 2: Enhanced Analysis
- 🔄 Advanced pattern recognition
- 🔄 Business rule extraction
- 🔄 Test scenario prioritization

### Phase 3: Test Data Generation
- 📋 XML test data generation
- 📋 Schema-compliant data creation
- 📋 Edge case data generation

### Phase 4: Production Features
- 📋 Web UI
- 📋 CI/CD integration
- 📋 Batch processing
- 📋 Test execution and validation

## Support

For issues and questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with details

## Examples

See the `examples/` directory for sample XSLT/XSD files and generated test cases.