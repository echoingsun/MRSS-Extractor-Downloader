import xml.etree.ElementTree as ET
import csv
import os

config = {
    'dir_path': '/Users/Lazybeam/Desktop/Work/YoungHollywood/xml/',
    'output_csv_path': '/Users/Lazybeam/Desktop/Work/YoungHollywood/syndication.csv'
}

video_list = []
processed = []
error_log = []


def main():
    # initialize xml file index
    file_index = 1

    # run for all xml files in the directory
    for filename in os.listdir(config['dir_path']):

        if filename.endswith('.xml'):
            print('-----------------')
            print('Processing: no.' + str(file_index) + ' xml file')

            xml_parse_path = config['dir_path'] + filename
            root = xml_parsing(xml_parse_path)
            extract_video_info(filename, root)

            processed.append(filename)

            file_index = file_index + 1

    for item in video_list:
        item['no'] = str(video_list.index(item) + 1)

    # batch write to csv
    write_to_csv()


def xml_parsing(file_path):
    try:
        # parse xml file
        tree = ET.parse(file_path)
        root = tree.getroot()
        print('Successfully parsed' + file_path)

        return root

    except Exception as error:
        print(error)
        error_log.append(error)


def extract_video_info(filename, root):
    # initialize indices
    channel = root[0]
    no_of_lists = len(channel)

    item_start_index = 0
    item_end_index = 0
    media_url_index = 0
    title_index = 0
    description_index = 0
    thumbnail_index = 0
    keyword_index = 0

    try:

        for i in range(no_of_lists):
            if channel[i].tag == 'item':
                item_start_index = i
                break
            else:
                i = i + 1

        for i in range(no_of_lists):
            if channel[i].tag == 'item':
                item_end_index = i
            else:
                i = i + 1

        for i in range(len(channel[item_start_index])):
            if channel[item_start_index][i].tag == 'title':
                title_index = i
            if channel[item_start_index][i].tag == 'description':
                description_index = i
            if channel[item_start_index][i].tag.endswith('thumbnail'):
                thumbnail_index = i
            if channel[item_start_index][i].tag.endswith('keywords'):
                keyword_index = i
            if channel[item_start_index][i].tag.endswith('group'):
                media_url_index = i
                break
            else:
                i = i + 1

        # extract metadata and put into video_list
        for i in range(item_start_index, item_end_index + 1):
            dict_info = {}

            j = i - item_start_index + 1
            dict_info['no'] = 0
            dict_info['topic'] = filename.split('.')[0]
            dict_info['topic_no'] = j
            dict_info['title'] = channel[i][title_index].text
            dict_info['description'] = channel[i][description_index].text
            dict_info['thumbnail_url'] = channel[i][thumbnail_index].attrib['url']
            dict_info['keywords'] = channel[i][keyword_index].text
            dict_info['video_url'] = channel[i][media_url_index][0].attrib['url']

            video_list.append(dict_info)

        print('Successfully extracted video info for ' + filename)

    except Exception as error:
        print(error)
        error_log.append(error)


def write_to_csv():
    output_csv_path = config['output_csv_path']

    try:
        with open(output_csv_path, 'r', encoding='ISO-8859-1') as f1:
            existing = csv.DictReader(f1)
            headers = existing.fieldnames
            f1.close()

        with open(output_csv_path, 'w', encoding='utf-8') as f2:
            writer = csv.DictWriter(f2, fieldnames=headers)
            writer.writeheader()
            writer.writerows(video_list)
            print('\n\nSuccessfully registered video info for ' + str(len(processed)) + ' xml files')

    except Exception as error:
        print(error)
        error_log.append(error)


if __name__ == "__main__":
    main()
