# Pan OpenAI Analysis Function

## Overview
This Azure Function provides intelligent, context-aware analysis of receipt data using OpenAI's GPT-4. It processes structured data from Google Vision AI, extracts key receipt information, and adds witty commentary through a personalized AI persona.

## Key Features
- HTTP-triggered execution
- GPT-4 powered analysis
- Sarcastic financial advisor persona
- Structured JSON output
- Dual storage strategy (active/archive)
- Automatic form generation trigger
- Comprehensive error handling

## Technical Details

### Environment Variables
```
OPENAI_API_KEY=your_openai_key
AzureWebJobsStorage=your_storage_connection
FORM_EDIT_URL=next_function_url
```

### Blob Storage Structure
- Input Source:
  - URL: `process/latest_result.json`
- Output Containers:
  - Open Container: 
    - `analysis.json`: Current analysis results
  - Open-Archive Container:
    - `analysis_[timestamp].json`: Timestamped archives

### Function Configuration
- Trigger: HTTP (Anonymous)
- Route: `aiopen_process`
- Model: GPT-4
- Temperature: 0 (for consistent results)

### AI Persona
The function implements a witty, sarcastic financial advisor who:
- Extracts essential receipt information
- Adds humorous commentary about purchases
- Maintains professional accuracy while being entertaining
- Provides context-aware financial observations

### Data Processing
Extracts standardized fields:
- vendor_name
- address
- phone
- date
- tax
- total
- category
- commentary (witty financial observation)

### Processing Steps
1. Validates environment configuration
2. Retrieves Vision AI results from blob storage
3. Processes data through GPT-4 with custom prompt
4. Structures response as standardized JSON
5. Stores results in both active and archive containers
6. Triggers form generation endpoint

## Pipeline Integration

### Previous Stage
Processes Vision AI results from:
[pan-goog Repository](https://github.com/Fruitloop24/pan-goog)

### Next Stage
Triggers form generation:
[pan-form Repository](https://github.com/Fruitloop24/pan-form)

### Data Flow
1. Receives HTTP trigger (from Vision processing)
2. Downloads latest Vision AI results
3. Processes through GPT-4
4. Stores structured analysis
5. Triggers form generation

## Deployment Requirements
- Azure Functions Core Tools
- Python 3.9+
- Azure Storage Account
- OpenAI API access
- Azure Storage containers configured

## Local Development
1. Clone the repository
2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Set up local.settings.json with required environment variables
5. Start the function:
```bash
func start
```

## Security Notes
- OpenAI API key should be secured in environment variables
- Anonymous HTTP trigger for pipeline integration
- Credentials should never be committed to the repository
- Implement proper RBAC in production environments

## Error Handling
- Environment validation
- HTTP request errors
- JSON parsing errors
- OpenAI API errors
- Storage operation errors
- Form trigger failures (non-blocking)
- Detailed error logging

## Contributing
Contributions welcome! Please read the contributing guidelines and submit pull requests for any improvements.

## License
MIT License - see LICENSE file for details