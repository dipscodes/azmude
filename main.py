from multiprocessing import Pool

def process_page_index(index):
    print("actress page index: ", index)


if __name__ == '__main__':
    start_index = 51
    end_index = 60
    num_processes = 2  # You can adjust this value based on your CPU cores
    p = Pool(2)

    p.map(process_page_index, range(start_index, end_index + 1))
