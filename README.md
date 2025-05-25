# XML Chunker

A Streamlit application for parsing XSD schemas and generating dummy XML files.

## Features

- Select a folder containing multiple XSD files
- Browse and select specific XSD files from the chosen folder
- View the selected XSD file in the UI
- Generate dummy XML files based on the selected XSD schema

## Installation

1. Clone the repository:
```bash
git clone https://github.com/siddswork/xml_chunker.git
cd xml_chunker
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Use the file explorer to select a folder containing XSD files
3. Choose a specific XSD file from the list
4. View the XSD file content in the UI
5. Click the "Generate XML" button to create a dummy XML file based on the selected XSD

## Testing

The application can be tested using the XSD files in the `resource/21_3_5_distribution_schemas` folder. 
For example, you can select the `IATA_OrderCreateRQ.xsd` file from this folder to test the application.

## Project Structure

```
xml_chunker/
├── app.py                  # Main Streamlit application
├── utils/
│   ├── __init__.py
│   ├── xsd_parser.py       # XSD parsing utilities
│   └── xml_generator.py    # XML generation utilities
├── resource/               # Sample XSD files for testing
│   └── 21_3_5_distribution_schemas/
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```
