# Agentic XSLT Test Generator

A sophisticated multi-agent system for generating comprehensive XSLT test cases using OpenAI's o4-mini for systematic reasoning and GPT-4.1 for complex business logic understanding.

## 🎯 Project Overview

This system replicates and automates the manual XSLT analysis methodology that successfully generated 135+ test cases. It uses a 7-agent architecture to analyze XSLT transformations and generate comprehensive test scenarios.

### Target Goals
- **125+ Test Cases**: Generate comprehensive test coverage across 14 categories
- **Business Logic Coverage**: Extract 45+ specific business rules from XSLT logic
- **Systematic Analysis**: Follow proven progressive depth methodology
- **High Quality**: Produce realistic XML snippets with business validation

## 🏗️ Architecture

### 7-Agent System Design

1. **Orchestrator Agent** (GPT-4.1) - Workflow coordination and synthesis
2. **File Analyzer Agent** (o4-mini) - Progressive depth XSLT analysis
3. **Pattern Hunter Agent** (o4-mini) - Systematic pattern recognition
4. **Schema Mapper Agent** (o4-mini) - XSD structure analysis
5. **Cross-Reference Validator** (o4-mini) - Multi-file validation
6. **Business Logic Extractor** (GPT-4.1) - Deep business understanding
7. **Test Case Generator** (GPT-4.1) - Comprehensive test creation

### Model Optimization
- **o4-mini**: Systematic analysis, pattern recognition, validation
- **GPT-4.1**: Complex orchestration, business logic, creative test generation

## 📁 Project Structure

```
agentic_test_gen/
├── agentic_test_gen/           # Main package
│   ├── core/                   # Core framework
│   │   ├── base_agent.py       # Base agent classes
│   │   ├── communication_bus.py # Inter-agent messaging
│   │   └── knowledge_base.py   # Shared data storage
│   ├── agents/                 # Agent implementations
│   │   ├── orchestrator.py     # Orchestrator Agent (GPT-4.1)
│   │   └── file_analyzer.py    # File Analyzer Agent (o4-mini)
│   ├── config/                 # Configuration
│   │   └── settings.py         # System settings
│   ├── utils/                  # Utilities
│   │   └── logging.py          # Logging setup
│   └── system.py               # Main orchestration
├── docs/                       # Documentation
│   ├── AGENTIC_SYSTEM_DESIGN.md
│   └── IMPLEMENTATION_PLAN.md
├── alt_analysis/               # Manual analysis methodology
│   ├── methodology/            # Analysis logs and instructions
│   └── test_cases/             # Generated test cases (177 total)
├── cli.py                      # Command line interface
└── README.md                   # This file
```

## 🚀 Getting Started

### Prerequisites

1. **Python 3.9+**
2. **OpenAI API Key** with access to GPT-4.1 and o4-mini models
3. **Required packages**:
   ```bash
   pip install openai lxml pathlib asyncio
   ```

### Setup

1. **Set your OpenAI API key**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. **Clone and navigate to the project**:
   ```bash
   cd /home/sidd/dev/xml_chunker/agentic_test_gen
   ```

### Running the Demo

```bash
python cli.py
```

This will:
- Initialize the agentic system
- Run Phase 1 analysis (Orchestrator + File Analyzer)
- Generate analysis plan and XSLT structure analysis
- Save results to `agentic_test_results.json`

## 📊 Current Status: Phase 1 Implementation

### ✅ Completed (Phase 1)
- [x] Core agent framework with base classes
- [x] Inter-agent communication bus
- [x] Shared knowledge base system
- [x] Orchestrator Agent (GPT-4.1) for strategic planning
- [x] File Analyzer Agent (o4-mini) for systematic XSLT analysis
- [x] Configuration management
- [x] Logging and error handling
- [x] CLI demo interface

### 🚧 In Progress (Phase 2-4)
- [ ] Pattern Hunter Agent (o4-mini)
- [ ] Schema Mapper Agent (o4-mini)
- [ ] Cross-Reference Validator Agent (o4-mini)
- [ ] Business Logic Extractor Agent (GPT-4.1)
- [ ] Test Case Generator Agent (GPT-4.1)
- [ ] Analysis caching system

### 📋 Planned (Future Phases)
- [ ] XSLT refactoring recommendations
- [ ] XSD simplification suggestions
- [ ] Mapping specification generation
- [ ] Performance optimization
- [ ] Web interface

## 🎯 Implementation Roadmap

### Phase 1: Core Framework (Weeks 1-2) ✅
- Basic agent architecture
- Communication and knowledge systems
- Orchestrator and File Analyzer agents

### Phase 2: Pattern Recognition & Validation (Weeks 3-4)
- Pattern Hunter agent implementation
- Schema Mapper agent implementation
- Cross-Reference Validator agent implementation

### Phase 3: Business Logic & Test Generation (Weeks 5-6)
- Business Logic Extractor agent
- Test Case Generator agent
- Complete 14-category test generation

### Phase 4: Caching & Extended Capabilities (Weeks 7-8)
- Analysis caching system
- XSLT refactoring agent
- XSD simplification agent
- Mapping specification generator

## 🧪 Test Files

The system is designed to work with IATA NDC XSLT transformations. Test files are expected at:

- **XSLT**: `../resource/orderCreate/xslt/OrderCreate_MapForce_Full.xslt`
- **Input XSD**: `../resource/orderCreate/input_xsd/AMA_ConnectivityLayerRQ.xsd`
- **Output XSD**: `../resource/orderCreate/output_xsd/OrderCreateRQ.xsd`

## 📚 Documentation

### Design Documents
- [**System Design**](docs/AGENTIC_SYSTEM_DESIGN.md) - Complete architecture overview
- [**Implementation Plan**](docs/IMPLEMENTATION_PLAN.md) - 8-week development roadmap

### Analysis Methodology
- [**Manual Analysis Logs**](alt_analysis/methodology/) - Successful manual methodology
- [**Generated Test Cases**](alt_analysis/test_cases/) - 177 comprehensive test cases
- [**Analysis Instructions**](alt_analysis/methodology/detailed_read_instructions.md) - Step-by-step methodology

## 🔧 Configuration

Key settings in `agentic_test_gen/config/settings.py`:

```python
# Model Settings
o4_mini_model = "o1-mini"              # Actual OpenAI model
gpt41_model = "gpt-4-turbo-preview"    # Actual OpenAI model

# Quality Thresholds
min_test_cases = 125                   # Target test case count
min_business_rules = 45                # Minimum business rules to extract
min_pattern_coverage = 0.95            # Pattern coverage threshold

# Performance
max_concurrent_agents = 3              # Parallel agent execution
analysis_timeout = 300                 # 5 minute timeout per agent
```

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**:
   ```
   Error: OPENAI_API_KEY environment variable not set
   ```
   **Solution**: Set your OpenAI API key in environment variables

2. **File Not Found**:
   ```
   XSLT file not found: ../resource/orderCreate/xslt/...
   ```
   **Solution**: Ensure test files are in the correct relative path

3. **Model Access Error**:
   ```
   Error: Model 'gpt-4.1' not available
   ```
   **Solution**: Verify your API key has access to GPT-4 models

### Debug Mode

Enable debug logging:
```python
settings = AgenticSystemSettings()
settings.debug_mode = True
settings.verbose_logging = True
```

## 🤝 Contributing

This is Phase 1 of the implementation. Next steps:

1. **Implement Pattern Hunter Agent** using o4-mini for systematic pattern recognition
2. **Add Schema Mapper Agent** for comprehensive XSD analysis
3. **Integrate Cross-Reference Validator** for multi-file validation
4. **Complete Business Logic Extractor** using GPT-4.1
5. **Implement Test Case Generator** for final 125+ test case creation

## 📄 License

MIT License - See project root for details.

## 🎉 Success Metrics

The system aims to replicate the success of the manual methodology:

- **135+ Test Cases** generated manually across 14 categories
- **177 Total Test Cases** documented in alt_analysis
- **8 Major Business Logic Patterns** identified
- **45+ Specific Business Rules** extracted
- **Complete XSLT Coverage** with line-by-line traceability

Phase 1 establishes the foundation for achieving these metrics through automated agentic analysis.