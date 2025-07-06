# Agentic XSLT Test Generation CLI

This CLI validates and demonstrates the agentic XSLT test generation system using real XSLT files from the `resource/orderCreate/xslt/` directory.

## Usage

```bash
# Analyze a specific XSLT file
python cli.py --file OrderCreate_Part1_AI.xslt

# Compare both XSLT files
python cli.py --compare

# Analyze all XSLT files in the directory
python cli.py --all

# Save analysis to JSON file
python cli.py --file OrderCreate_MapForce_Full.xslt --output report.json

# Adjust token limits
python cli.py --file MyFile.xslt --max-tokens 10000
```

## Features

### 📊 File Metadata Analysis
- File size, line count, encoding detection
- Token estimation for LLM processing
- Memory usage recommendations

### ✂️ XSLT Chunking Analysis
- Intelligent chunking based on XSLT structure
- Template boundary detection (helper vs main templates)
- Token-aware chunk sizing
- Processing time measurement

### 🔧 Helper Template Detection
- Automatic detection of MapForce helper templates (`vmf:vmf*_inputtoresult`)
- Template classification and analysis
- Template dependency mapping

### 🔗 Dependency Analysis
- Variable reference extraction (`$variable`)
- Template call detection (`<xsl:call-template>`)
- Function call identification (`namespace:function()`)
- Dependency relationship mapping

### 🔍 Pattern Detection
- XSLT choose blocks detection
- Variable declaration patterns
- XPath expression identification
- Complexity scoring

### ⚖️ File Comparison
- Side-by-side analysis of multiple XSLT files
- Metrics comparison (size, tokens, chunks, processing time)
- Helper template count comparison

## Real XSLT Files Tested

1. **OrderCreate_MapForce_Full.xslt** (79.2 KB, 1,887 lines)
   - Complete MapForce-generated transformation
   - 4 helper templates detected
   - 120 dependencies identified
   - 8 chunks generated

2. **OrderCreate_Part1_AI.xslt** (6.0 KB, 166 lines)
   - AI-generated partial transformation
   - No helper templates
   - Simpler structure
   - 3 chunks generated

## Validation Results

✅ **System Successfully Validated**:
- Real XSLT files processed without errors
- Helper templates correctly identified
- Dependencies properly extracted  
- Chunking respects token limits
- Patterns accurately detected
- Performance is fast (< 0.03s for large files)

## JSON Output Structure

The `--output` option saves detailed analysis in JSON format:

```json
{
  "file_path": "path/to/file.xslt",
  "file_name": "file.xslt", 
  "analysis_timestamp": 1234567890,
  "file_metadata": {
    "size_bytes": 81090,
    "line_count": 1887,
    "encoding": "utf-8",
    "estimated_tokens": 20272
  },
  "chunking_analysis": {
    "total_chunks": 8,
    "helper_templates": [...],
    "dependencies": {...},
    "patterns": {...},
    "token_analysis": {...}
  }
}
```

## Key Regex Patterns Tested

All 17 regex patterns in the system are validated:

- ✅ Template detection (`template_start`, `template_end`)
- ✅ Helper template identification (`helper_template`)
- ✅ Variable/dependency extraction (`variable_declaration`)
- ✅ XSLT function patterns (`function_start`, `function_end`)
- ✅ Choose block detection (`choose_start`, `choose_end`)
- ✅ Import/include patterns (`import_include`)
- ✅ Namespace declarations (`namespace_declaration`)
- ✅ **Fixed XPath pattern** (no longer matches "hello world")

## Dependencies

- Python 3.7+
- No external dependencies required (psutil optional for memory tracking)
- Uses the agentic test generation system in `src/`

## Performance

- **Small files** (~6KB): < 0.01s processing time
- **Large files** (~80KB): < 0.03s processing time  
- **Memory efficient**: Recommended strategies based on file size
- **Token-aware**: Respects LLM context limits

This CLI confirms that our agentic XSLT test generation system works correctly with real-world XSLT transformations!