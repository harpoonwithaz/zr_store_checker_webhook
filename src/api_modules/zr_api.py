import requests
from requests.exceptions import (
    HTTPError,
    Timeout,
    ConnectionError,
    RequestException
)

def get_json(api_url, params = None, headers = None, timeout = 10, retries = 3, backoff_factor = 2):
    """
    Fetch JSON data from an API endpoint.

    Args:
        url (str): API endpoint URL.
        params (dict, optional): Query parameters to include in the GET request.
        headers (dict, optional): Custom headers (e.g., for authorization).
        timeout (int, optional): Timeout in seconds for each request attempt.
        retries (int, optional): Number of times to retry on recoverable errors.
        backoff_factor (int, optional): Multiplier for retry delay (e.g., 2 means exponential backoff).

    Returns:
        dict | None: Parsed JSON response from the API, or None if request fails.
    """

    attempt = 0
    while attempt < retries:
        try:
            print(f'Sending *GET* request to {api_url}')
            response = requests.get(api_url, params=params, headers=headers, timeout=timeout)
            print(f'API Response: "{response}"')
            response.raise_for_status()
            return response.json()
        except Timeout:
            print(f"Timeout occurred (attempt {attempt + 1}/{retries})")
        except ConnectionError:
            print(f"Connection error (attempt {attempt + 1}/{retries})")
        except HTTPError as e:
            print(f"HTTP error: {e}")
            break  # Don’t retry 4xx/5xx errors, they’re usually not temporary
        except ValueError:
            print("Response content is not valid JSON.")
            break
        except RequestException as e:
            print(f"Unexpected error: {e}")
            break

        # Exponential backoff before retrying
        attempt += 1
        if attempt < retries:
            sleep_time = backoff_factor ** attempt
            print(f"Retrying in {sleep_time}s...")
            import time
            time.sleep(sleep_time)
    
    
    
    
