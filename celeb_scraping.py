from multiprocessing import Pool
import datetime
import json
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os


def get_production_info(production):
    h4_element = production.find('h4')
    type = h4_element.span.text.strip().lower().replace(":", "").capitalize()
    title = h4_element.a.text.strip()
    release_info = h4_element.contents[-1].strip().strip('()')

    ongoing_pattern = re.compile(r'(\d{4})-')  # Matches "YYYY-"
    range_pattern = re.compile(r'(\d{4})-(\d{4})')  # Matches "YYYY-YYYY"
    year_pattern = re.compile(r'^(\d{4})$')  # Matches "YYYY"

    ongoing_match = ongoing_pattern.search(release_info)
    range_match = range_pattern.search(release_info)
    year_match = year_pattern.search(release_info)

    if range_match:
        start_year = range_match.group(1)
        end_year = range_match.group(2)
        ongoing = False
    elif ongoing_match:
        start_year = ongoing_match.group(1)
        end_year = None
        ongoing = True
    elif year_match:
        start_year = year_match.group(1)
        end_year = None
        ongoing = False
    else:
        start_year = None
        end_year = None
        ongoing = False

    result = {
        "type": type,
        "title": title,
        "start_year": start_year,
        "end_year": end_year,
        "ongoing": ongoing,
        "media_list": []
    }
    return result


def get_media_info(media):
    if (not media):
        return None
    if media.find('a', class_='video'):
        a_tag = media.find('a')
        href = a_tag.get('href')
        eid = a_tag.get('eid')
        img_src = a_tag.find('img')['src']
        result = {
            "link_to_media": href,
            "eid": eid,
            "image_source": img_src,
            "type": "video"
        }
        return result
    elif media.find('a', class_='picture'):
        a_tag = media.find('a')
        href = a_tag.get('href')
        img_src = a_tag.find('img')['src']
        result = {
            "link_to_media": href,
            "eid": None,
            "image_source": img_src,
            "type": "picture"
        }
        return result


def get_actress_portfolio(url, view_count):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    actress_name = soup.find('h1').text.strip()
    actress_name = re.sub(r'#.*', '', actress_name).strip()
    try:
        birthplace = soup.find(
            'div', class_='banner-info').find('a').text.strip()
    except:
        birthplace = ""
    # birthplace = soup.find('div', class_='banner-info').find('a').text.strip()
    hashtag = soup.find(
        'span', class_='tag-desktop').text.strip().replace("#", "")
    celeb_img_url = soup.find(
        'img', class_="img-circle pull-right img-responsive celeb-img").get('src')

    actress_portfolio = {
        "actress_name": actress_name,
        "birthplace": birthplace,
        "hashtag": hashtag,
        "celeb_img_url": celeb_img_url,
        "view_count": view_count,
        "url": url,
        "production_media_list": []
    }

    production_media_list = []
    production_section_list = soup.find_all('section')

    for production in production_section_list:
        media_div_for_section = production.find_next_sibling()
        production_info = get_production_info(production)

        if media_div_for_section and media_div_for_section.name == 'div':
            media_div_list = media_div_for_section.find_all(
                'div', class_='col-lg-3 col-sm-4 col-xs-6 celebs-boxes albuma')
            media_list = []
            for media in media_div_list:
                media_info = get_media_info(media)
                media_list.append(media_info)
            production_info["media_list"] = media_list

        production_media_list.append(production_info)

    actress_portfolio["production_media_list"] = production_media_list
    return actress_portfolio


def process_page_index(index):
    print("actress page index: ", index)
    popular_actress_url = f'https://www.aznude.com/browse/celebs/popular/{
        index}.html'
    response = requests.get(popular_actress_url)
    soup_popular_actress = BeautifulSoup(response.text, 'html.parser')
    actress_div_list = soup_popular_actress.find_all(
        'div', class_="col-lg-2 col-md-3 col-sm-4 col-xs-6 story-thumbs celebs-boxes")
    actress_portfolio_list = []
    failed_actress_portfolio_list = []

    in_page_index = 0

    for actress in actress_div_list:
        actress_url = actress.find('a').get('href')
        actress_name = actress.find('h4').text.strip()
        try:
            view_count = actress.find('span').text.strip()
            actress_portfolio = get_actress_portfolio(
                url="https://aznude.com" + actress_url, view_count=view_count)
            actress_portfolio_list.append(actress_portfolio)
            print(actress_name)
        except Exception as e:
            failed_stat = {
                "actress_url": "https://aznude.com" + actress_url,
                "actress_name": actress_name,
                "in_page_index": in_page_index,
                "page_index": index,
                "view_count": view_count,
                "error": str(e)
            }
            # print(failed_stat)
            failed_actress_portfolio_list.append(failed_stat)
            failed_json_string = json.dumps(failed_stat)
            with open(f'.\\failed_actress_list\\failed_{index}_{actress_name}.json', 'w') as failed_json_file:
                failed_json_file.write(failed_json_string)
            print(actress_name, "failed")
        in_page_index += 1

    json_string = json.dumps(actress_portfolio_list)
    with open(f'.\\actress_portfolio\\actress_portfolio_list_{index}.json', 'w') as json_file:
        json_file.write(json_string)

    return 0


if __name__ == '__main__':
    load_dotenv()
    start_index = int(os.getenv("START_INDEX"))
    end_index = int(os.getenv("END_INDEX"))
    num_processes = int(os.getenv("NUMBER_OF_PROCESSES"))
    
    scraping_starting_time = datetime.datetime.now()
        
    with Pool(num_processes) as p:
        p.map(process_page_index, range(start_index, end_index + 1))

    scraping_done_time = datetime.datetime.now()
    print(f"Starting Scraping from page {start_index} to {end_index} at {
          scraping_starting_time.strftime("%Y-%m-%d %H:%M:%S")}")
    print(f"Completed Scraping from page {start_index} to {end_index} at {
          scraping_done_time.strftime("%Y-%m-%d %H:%M:%S")}")

    print("Elapsed Time: ", scraping_done_time - scraping_starting_time)
