from dotenv import load_dotenv
import os


def process_page_index(index):
    print("actress page index: ", index)


if __name__ == '__main__':
    load_dotenv()
    start_index = os.getenv("START_INDEX")
    end_index = os.getenv("END_INDEX")
    print(start_index, end_index)
