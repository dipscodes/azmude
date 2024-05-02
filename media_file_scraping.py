
from multiprocessing import Pool
import datetime
import json
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os


def complete_links(link):
    if (link.startswith("/") and not link.startswith("//")):
        return "https://www.aznude.com" + link

    elif (link.startswith("//")):
        return "https:" + link

    elif link.startswith("https") or link.startswith("http"):
        return link


def index_to_file_path(index):
    return os.path.join('.', 'actress_portfolio', f'actress_portfolio_list_{index}.json')


def index_to_save_file_path(index):
    return os.path.join('.', 'updated_pages', f'actress_portfolio_list_{index}.json')


def get_media_file_link_and_tags(video_url):
    response = requests.get(video_url)
    video_soup = BeautifulSoup(response.text, 'html.parser')

    actress_video_tag_list = []
    tag_error = ""
    link_error = ""

    try:
        actress_video_h2_element = video_soup.find_all(
            'h2', class_="video-tags")[0]
        actress_video_tag_element_list = actress_video_h2_element.find_all('a')
        for tag in actress_video_tag_element_list:
            actress_video_tag_list.append({
                "name": tag.text.strip(),
                "link": complete_links(tag.get('href'))
            })
    except Exception as e:
        tag_error = str(e)

    download_link = ""

    try:
        download_div = video_soup.find_all('div', class_='videoButtons')
        for div in download_div:
            if div.text == 'Download':
                download_link = complete_links(div.parent.get('href'))
    except Exception as e:
        link_error = str(e)

    return {
        "tag_list": actress_video_tag_list,
        "media_file_link": download_link,
        "tag_error": tag_error,
        "link_error": link_error
    }


def get_all_actress_portfolio_file():
    folder_path = os.path.join('.', 'actress_portfolio')
    try:
        files = os.listdir(folder_path)
        return files
    except FileNotFoundError:
        print(f"Error: The folder '{folder_path}' does not exist.")
        return []


def read_json_file(file_path):
    """
    Reads a JSON file and returns its content as a Python dictionary.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The content of the JSON file as a dictionary.
        None: If the file cannot be opened or the JSON data is invalid.
    """

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}")
        return None


def add_meadia_file_link_and_tags_to_page(index):
    portfolio_page_file_path = index_to_file_path(index)
    page_content = read_json_file(portfolio_page_file_path)
    for actress in page_content:
        print(actress["actress_name"])
        production_media_list = actress["production_media_list"]
        for production in production_media_list:
            print("    " + production["title"])
            media_list = production["media_list"]
            for media in media_list:
                if media["type"] == "video":
                    link_to_media = complete_links(media["link_to_media"])
                    eid = complete_links(media["eid"])
                    image_source = complete_links(media["image_source"])
                    link_and_tags = get_media_file_link_and_tags(
                        video_url=link_to_media)

                    media["link_to_media"] = link_to_media
                    media["eid"] = eid
                    media["image_source"] = image_source
                    media["tag_list"] = link_and_tags["tag_list"]
                    media["media_file_link"] = link_and_tags["media_file_link"]
                    media["tag_error"] = link_and_tags["tag_error"]
                    media["link_error"] = link_and_tags["link_error"]
            # break
        # break
    return page_content


def save_updated_page(index):
    page_content = add_meadia_file_link_and_tags_to_page(index)
    json_string = json.dumps(page_content)
    with open(index_to_save_file_path(index), 'w') as json_file:
        json_file.write(json_string)


if __name__ == '__main__':
    load_dotenv()
    start_index = int(os.getenv("START_INDEX"))
    end_index = int(os.getenv("END_INDEX"))
    num_processes = int(os.getenv("NUMBER_OF_PROCESSES"))

    scraping_starting_time = datetime.datetime.now()

    save_updated_page(15)

    # with Pool(num_processes) as p:
    #     p.map(save_updated_page, range(start_index, end_index + 1))

    scraping_done_time = datetime.datetime.now()
    print("\n")

    print(f"Starting Scraping from page {start_index} to {end_index} at {
          scraping_starting_time.strftime("%Y-%m-%d %H:%M:%S")}")
    print(f"Completed Scraping from page {start_index} to {end_index} at {
          scraping_done_time.strftime("%Y-%m-%d %H:%M:%S")}")

    print("Elapsed Time: ", scraping_done_time - scraping_starting_time)
