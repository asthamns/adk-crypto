import nltk
from pathlib import Path
import ssl
import certifi

def download_nltk_data():
    """
    This script ensures that the necessary NLTK data packages ('punkt', 'stopwords')
    are downloaded to a predictable, user-writable location. It also handles
    potential SSL certificate issues.
    """
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

    # Create a specific, known folder in your user directory.
    nltk_data_path = Path.home() / "nltk_data"
    
    print(f"--- NLTK data directory will be: {nltk_data_path} ---")

    # Create the directory if it doesn't exist.
    nltk_data_path.mkdir(exist_ok=True)
    
    # Add the path to NLTK's search list to ensure it's found.
    if str(nltk_data_path) not in nltk.data.path:
        nltk.data.path.append(str(nltk_data_path))
    
    print("--- Starting NLTK data download... ---")
    
    packages = ['punkt', 'stopwords']
    all_successful = True
    
    for package in packages:
        try:
            print(f"Downloading '{package}'...")
            nltk.download(package, download_dir=str(nltk_data_path))
            print(f"Successfully downloaded '{package}'.")
        except Exception as e:
            print(f"!!! FAILED to download '{package}'. Error: {e} !!!")
            all_successful = False

    if all_successful:
        print("\n--- All NLTK data packages downloaded successfully. ---")
        print(f"--- They are located in: {nltk_data_path} ---")
        print("--- You can now restart the ADK application. ---")
    else:
        print("\n--- Some packages failed to download. Please check your network connection/firewall and try again. ---")

if __name__ == "__main__":
    download_nltk_data() 