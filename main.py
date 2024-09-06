import json
import re
import os
import sys
import subprocess
import shutil
import argparse

from safaribooks import SafariBooks


def unwrap_cookies(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        request_cookies = data.get('Request Cookies', {})
        return request_cookies


def write_cookies_to_file(cookies_dict, output_file_path):
    with open(output_file_path, 'w') as file:
        json.dump(cookies_dict, file, indent=4)


def extract_value_from_url(url):
    pattern = r'/(\d+)/?$'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        return None


def find_epub_files(directory):
    epub_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.epub'):
                epub_files.append(os.path.join(root, file))
    return epub_files


def copy_file_to_directory(source, destination_dir):
    try:
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        destination_file = os.path.join(destination_dir, os.path.basename(source))
        shutil.copy(source, destination_file)

        print(f"File '{os.path.basename(source)}' copied to '{destination_dir}' successfully.")
    except IOError as e:
        print(f"Unable to copy file. {e}")


def download(book_list):
    with open(book_list) as file:
        for line in file:
            url = line.strip()
            print(url)
            if url:
                book_id = extract_value_from_url(url)
                try:
                    # subprocess.run([sys.executable, "./safaribooks.py", "--kindle", book_id], check=True)
                    ns = Namespace(book_id)
                    SafariBooks(ns)
                except subprocess.CalledProcessError as e:
                    print("Error:", e)

class Namespace:
    def __init__(self, bookid):
        self.cred = None
        self.login = False
        self.no_cookies = False
        self.kindle = True
        self.log = True
        self.bookid = bookid


if __name__ == "__main__":

    # copy the cookies file that was manually copied into the cookies file passed into the container
    starting_cookies = unwrap_cookies("./resources/cookies.json")
    write_cookies_to_file(starting_cookies, "./resources/cookies.json")

    # read the book list file passed into the container and download each book
    book_list = "./resources/book_list.md"
    download(book_list)

    directory_path = "./safaribooks/"
    downloads_path = "./book_downloads"

    # copy the books out of the container
    epub_files_list = find_epub_files(directory_path)
    for e in epub_files_list:
        copy_file_to_directory(e, downloads_path)
