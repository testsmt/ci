import requests
import zipfile
import tarfile
import os
import shutil

def download_file(url, local_filename):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

def extract_zip(file_path, extract_to='.', rename_to=None):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    if rename_to:
        extracted_folder = os.path.join(extract_to, os.path.splitext(os.path.basename(file_path))[0])
        new_folder_path = os.path.join(extract_to, rename_to)
        shutil.move(extracted_folder, new_folder_path)

def extract_tar_gz(file_path, extract_to='.', rename_to=None):
    with tarfile.open(file_path, 'r:gz') as tar_ref:
        tar_ref.extractall(extract_to)
    if rename_to:
        extracted_folder = os.path.join(extract_to, os.path.splitext(os.path.basename(file_path))[0])
        new_folder_path = os.path.join(extract_to, rename_to)
        shutil.move(extracted_folder, new_folder_path)

def extract_tar_bz2(file_path, extract_to='.', rename_to=None):
    with tarfile.open(file_path, 'r:bz2') as tar_ref:
        tar_ref.extractall(extract_to)
    if rename_to:
        extracted_folder = os.path.join(extract_to, os.path.splitext(os.path.basename(file_path))[0])
        new_folder_path = os.path.join(extract_to, rename_to)
        shutil.move(extracted_folder, new_folder_path)

def extract_file(file_path, extract_to='.', rename_to=None):
    if file_path.endswith('.zip'):
        print(f"Extracting ZIP file: {file_path}")
        extract_zip(file_path, extract_to, rename_to)
    elif file_path.endswith('.tar.gz'):
        print(f"Extracting TAR.GZ file: {file_path}")
        extract_tar_gz(file_path, extract_to, rename_to)
    elif file_path.endswith('.tar.bz2'):
        print(f"Extracting TAR.BZ2 file: {file_path}")
        extract_tar_bz2(file_path, extract_to, rename_to)
    else:
        raise ValueError(f"Unsupported file type for {file_path}")

    os.remove(file_path)
    print(f"Removed archive file: {file_path}")