import logging
import azure.functions as func
import os
import json
from openai import AsyncOpenAI
from azure.storage.blob import BlobServiceClient
from datetime import datetime
import requests

# Initialize the function app
app = func.FunctionApp()

# Environment Variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AzureWebJobsStorage")
FORM_EDIT_URL = os.getenv("FORM_EDIT_URL")

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

@app.function_name(name="aiopen_process")
@app.route(route="aiopen_process", auth_level=func.AuthLevel.ANONYMOUS)
async def aiopen_process(req: func.HttpRequest) -> func.HttpResponse:
    """Process JSON data with OpenAI and save to output containers"""
    logging.info("Function aiopen_process triggered")
    
    try:
        # Verify environment variables
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        if not AZURE_STORAGE_CONNECTION_STRING:
            raise ValueError("AzureWebJobsStorage environment variable is not set")

        # Download JSON from URL
        url = "https://panstorage.blob.core.windows.net/process/latest_result.json"
        logging.info(f"Attempting to download JSON from {url}")
        
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        logging.info(f"Successfully downloaded JSON data: {json.dumps(data)[:200]}...")  # Log first 200 chars

        # Process with OpenAI
        logging.info("Sending request to OpenAI")
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a witty, sarcastic financial advisor who extracts receipt details. "
                    "First extract these fields: vendor_name, address, phone, date, tax, total, category. "
                    "Then add a 'commentary' field with a short, sarcastic observation about the purchase - "
                    "be playfully judgmental but keep it light and funny. "
                    "Format everything as a single valid JSON object with these exact fields: "
                    "vendor_name, address, phone, date, tax, total, category, commentary"
                )
            },
            {
                "role": "user",
                "content": f"Extract details from this receipt data:\n{json.dumps(data, indent=2)}"
            }
        ]
        
        completion = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0
        )
        
        processed_data = json.loads(completion.choices[0].message.content.strip())
        logging.info(f"Successfully processed data with OpenAI: {json.dumps(processed_data)[:200]}...")

        # Initialize blob service client
        blob_service = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        
        # Save to output container
        output_container = blob_service.get_container_client("open")
        output_blob = output_container.get_blob_client("analysis.json")
        output_blob.upload_blob(json.dumps(processed_data, indent=2), overwrite=True)
        logging.info("Saved analysis.json to 'open' container")

        # Save to archive
        archive_container = blob_service.get_container_client("open-archive")
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        archive_blob = archive_container.get_blob_client(f"analysis_{timestamp}.json")
        archive_blob.upload_blob(json.dumps(processed_data, indent=2))
        logging.info(f"Saved analysis_{timestamp}.json to 'open-archive' container")

        # Trigger form_edit endpoint with empty POST
        try:
            form_response = requests.post(FORM_EDIT_URL)
            form_response.raise_for_status()
            logging.info("Successfully triggered form_edit endpoint")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to trigger form_edit endpoint: {str(e)}")
            # Continue execution even if trigger fails
            pass

        return func.HttpResponse(
            json.dumps({"status": "success", "data": processed_data}),
            mimetype="application/json",
            status_code=200
        )
        
    except requests.exceptions.RequestException as e:
        error_message = f"Error downloading JSON: {str(e)}"
        logging.error(error_message)
        return func.HttpResponse(
            json.dumps({"status": "error", "message": error_message}),
            mimetype="application/json",
            status_code=500
        )
    except json.JSONDecodeError as e:
        error_message = f"Error parsing JSON: {str(e)}"
        logging.error(error_message)
        return func.HttpResponse(
            json.dumps({"status": "error", "message": error_message}),
            mimetype="application/json",
            status_code=500
        )
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        logging.error(error_message)
        return func.HttpResponse(
            json.dumps({"status": "error", "message": error_message}),
            mimetype="application/json",
            status_code=500
        )