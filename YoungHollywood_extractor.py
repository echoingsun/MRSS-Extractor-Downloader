import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as BS
import urllib.request
from datetime import datetime, date
import csv

config = {
    'feed_root': 'https://syndication.brightcove-services.com/v1/syndication/accounts/44143148/feeds/syndication1?key=57e411d6-5ba3-40ff-ae5a-781f61e9bdbc',
    'output_csv_dir': '/Users/Lazybeam/Desktop/Work/MCP/YoungHollywood/',
    'log_path': '/Users/Lazybeam/Desktop/Work/MCP/YoungHollywood/log.txt',
    'tags': ['title', 'pubdate', 'guid', 'duration'],
    'content_tag': 'group',
    'csv_headers': ['extraction_date', 'category', 'id', 'duration', 'yh_pub_date', 'title', 'video_url',
                    'thumbnail_url'],
    'keywords': ['internet%20celebrities', 'social%20media%20stars', 'online%20personalities', 'kpop', 'k-pop', 'music',
                 'sports', 'food', 'tv/film', 'fashion', 'gaming', 'younger%20hollywood', 'younger'],
    'yh_category_mapping': {
        'celeb': ['internet%20celebrities', 'social%20media%20stars'],
        'online_personalities': ['online%20personalities'],
        'kpop': ['kpop', 'k-pop'],
        'music': ['music'],
        'sports': ['sports'],
        'food': ['food'],
        'tv': ['tv/film', 'younger'],
        'fashion': ['fashion'],
        'gaming': ['gaming'],
        'younger_hollywood': ['younger%20hollywood']
    }
}

today = str(date.today())
ts = today + '_' + str(datetime.utcnow().strftime('%y_%m_%d_%H_%M_%S'))


def main():
    feed_list = generate_feed()

    log_text = open_log(config['log_path'])

    item_list = []

    # extract from xml file
    for feed in feed_list:
        category = feed[0]
        feed_link = feed[1]

        print('Now extracting: \n%s: %s' % (category, feed_link))

        html = urllib.request.urlopen(feed_link)
        table = open_html(html)

        extract_metadata(item_list, category, table, log_text)

    # write to log and csv
    write_to_log(item_list)
    write_to_csv(item_list)


def generate_feed():
    feed_list = []

    root_url = config['feed_root']
    limit = str(200)
    offset = str(0)

    feed_list.append(('general', root_url + '&limit=200&offset=0'))

    for keyword in config['keywords']:
        category = get_category(keyword)
        link = '%s&q=tags:%s&limit=%s&offset=%s' % (root_url, keyword, limit, offset)
        feed_list.append((category, link))

    return feed_list


def get_category(string):
    # mapping categories

    found = False

    for category, keywords in config['yh_category_mapping'].items():

        if not found:
            for keyword in keywords:
                if string.lower().find(keyword) >= 0:
                    found = True
                    return category
    if not found:
        return 'general'


def extract_metadata(item_list, category, table, log_text):
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

            item_dict['category'] = category

            item_string = str(BS(item, 'xml'))
            item_tree = ET.fromstring(item_string)

            for child in item_tree:
                #
                # print(child.tag, child.attrib)

                if child.tag in config['tags']:
                    if child.tag == 'pubdate':
                        item_dict['yh_pub_date'] = str(child.text)[5:16]
                    if child.tag == 'duration':
                        item_dict[child.tag] = round(float(child.text) / 1000, 2)
                    else:
                        item_dict[child.tag] = child.text
                elif child.tag == 'group':
                    for kid in child:
                        if 'url' in kid.attrib.keys():
                            item_dict['video_url'] = kid.attrib['url']
                elif child.tag == 'thumbnail':
                    item_dict['thumbnail_url'] = child.attrib['url']

            # print(item_dict)

            item_list.append(item_dict)


def open_log(log_path):
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            log_text = str(list(f))
            f.close()
            return log_text
    except Exception as error:
        print(error)


def open_html(html):
    # extract from body, all the items with 'item' tag
    soup = BS(html, "html.parser")
    table = soup.findAll("item")

    return table


def existing(string, log_text):
    # search the guid in the log
    if log_text.find(string) >= 0:
        return True
    else:
        return False


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
        output_csv_path = str(config['output_csv_dir']) + ts + '.csv'

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
