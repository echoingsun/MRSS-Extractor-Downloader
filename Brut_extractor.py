import urllib.request
from bs4 import BeautifulSoup as BS
import xml.etree.ElementTree as ET
from datetime import datetime, date
import csv

config = {
    'brut_url': 'https://api.brut.media/v1/rss?auth=73mJLEtY9fPlZXRhCY66FCEMDeCCPUI45I9VdFF94Tt8RYqfWC',
    'output_csv_dir': '/Users/Lazybeam/Desktop/Work/Brut/',
    'log_path': '/Users/Lazybeam/Desktop/Work/Brut/log.txt',
    'tags': ['title', 'description', 'category', 'pubdate', 'guid'],
    'content_tag': 'content',
    'csv_headers': ['id', 'extraction_date', 'category', 'duration', 'brut_pub_date', 'title', 'video_url',
                    'thumbnail_url'],
    'brut_category_mapping': {
        'entertainment': ['entertainment'],
        'news': ['news', 'economy'],
        'lifestyle': ['lifestyle', 'health'],
        'tech': ['science', 'technology', 'tech'],
        'sports': ['sport', 'sports'],
        'worldwide': ['international']
    }
}

today = str(date.today())
ts = today + '_' + str(datetime.utcnow().strftime('%y_%m_%d_%H_%M_%S'))


def main():

    # read extraction log to avoid duplicates
    log_text = open_log(config['log_path'])

    # open and read html
    html = urllib.request.urlopen(config['brut_url'])
    table = open_html(html)

    # extract from xml file
    item_list = extract_metadata(table, log_text)

    # write to log and csv
    write_to_log(item_list)
    write_to_csv(item_list)


def open_html(html):

    # extract from body, all the items with 'item' tag
    soup = BS(html, "html.parser")
    table = soup.findAll("item")

    return table


def extract_metadata(table, log_text):

    # create list for the current batch
    item_list = []

    for i, item in enumerate(table):

        item = str(item)

        # each item is an xml string
        item_string = str(BS(item, 'xml'))
        item_tree = ET.fromstring(item_string)

        # if the item is existing in log, skip
        if not existing(item_tree.find('guid').text, log_text):

            item_dict = {}
            item_id = int(i + 1)
            item_dict['id'] = item_id
            item_dict['extraction_date'] = today

            item_dict['ts'] = ts

            item_string = str(BS(item, 'xml'))
            item_tree = ET.fromstring(item_string)

            for child in item_tree:
                if child.tag in config['tags']:
                    if child.tag == 'pubdate':
                        item_dict['brut_pub_date'] = str(child.text)[5:16]
                    if child.tag == 'category':
                        item_dict['category'] = decide_category(child.text)
                    else:
                        item_dict[child.tag] = child.text
                elif child.tag == config['content_tag']:
                    item_dict['duration'] = child.attrib['duration']
                    item_dict['video_url'] = child.attrib['url']
                    for kid in child:
                        item_dict['thumbnail_url'] = kid.attrib['url']

            item_list.append(item_dict)

    print('Extacted ' + str(len(item_list)) + ' items for this batch.')
    return item_list


def open_log(log_path):
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            log_text = str(list(f))
            f.close()
            return log_text
    except Exception as error:
        print(error)


def existing(string, log_text):

    # search the guid in the log
    if log_text.find(string) >= 0:
        return True
    else:
        return False


def decide_category(string):

    # mapping categories

    found = False

    for category, keywords in config['brut_category_mapping'].items():

        if not found:
            for keyword in keywords:
                if string.lower().find(keyword) >= 0:
                    found = True
                    return category
    if not found:
        return 'others'


def write_to_log(item_list):
    if not item_list:
        return
    else:
        try:
            with open(config['log_path'], 'a', newline='', encoding='utf-8') as f:
                for row in item_list:
                    guid = row['guid']
                    string = ts + ',' + guid
                    f.write(string + '\n')
                f.close()
        except Exception as error:
            print(error)


def write_to_csv(item_list):
    if not item_list:
        return
    else:
        output_csv_path = config['output_csv_dir'] + ts + '.csv'

        try:
            with open(output_csv_path, 'w', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=config['csv_headers'], extrasaction='ignore')
                writer.writeheader()
                writer.writerows(item_list)
            f.close()

        except Exception as error:
            print(error)


if __name__ == "__main__":
    main()
