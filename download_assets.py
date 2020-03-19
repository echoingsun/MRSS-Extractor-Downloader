import urllib.request
import csv

environment = {
    'cloud-drive': {
        'csv_file_path': '/Users/Lazybeam/Desktop/Work/YoungHollywood/syndication.csv',
        'thumbnail_download_dir': '/Users/Lazybeam/Google Drive File Stream/My Drive/provider-videos-YH/thumbnails/',
        'video_download_dir': '/Users/Lazybeam/Google Drive File Stream/My Drive/provider-videos-YH/videos/'
    },
    'local': {
        'csv_file_path': '/Users/Lazybeam/Desktop/Work/YoungHollywood/test.csv',
        'thumbnail_download_dir': '/Users/Lazybeam/Desktop/Work/YoungHollywood/output/',
        'video_download_dir': '/Users/Lazybeam/Desktop/Work/YoungHollywood/output/'
    }

}

error_log = []

# switch if cloud drive is full
config = environment['local']


def main():

    # video_list holds all info
    video_list = []
    headers = load_csv((config['csv_file_path']), video_list)

    # for each item in video_list, download thumbnail and video and write to csv
    download_assets(video_list, headers)

    if not error_log:
        print('\n--------------------')
        print('Sucessfully downloaded assets')
    else:
        print(error_log)


def load_csv(file_path, video_list):
    with open(file_path, 'r', encoding='ISO-8859-1') as f1:
        reader = csv.DictReader(f1)
        headers = reader.fieldnames

        for item in reader:
            video_list.append(item)

        f1.close()

        return headers


def download_assets(video_list, headers):
    for i, row in enumerate(video_list):
        print('--------------------')
        print('Now processing: no.' + str(i + 1))

        existing = bool(row['thumbnail_file']) and bool(row['video_file'])

        if existing:
            print('existing')
            if i + 1 == len(video_list):
                break
            else:
                continue
        else:
            download_line(row, video_list, headers)


def download_line(row, video_list, headers):

    # get metadata
    title = row['title']
    topic = row['topic']
    topic_no = row['topic_no']
    thumbnail_url = row['thumbnail_url']
    video_url = row['video_url']

    media_id = video_url.split('media/')[1].split('/')[0]

    string = topic + '-' + topic_no + '-' + media_id

    # set destination path
    thumbnail_file_name = string + '.jpg'
    video_file_name = string + '.mp4'

    thumbnail_file_path = config['thumbnail_download_dir'] + thumbnail_file_name
    video_file_path = config['video_download_dir'] + video_file_name

    # download thumbnail and update video_list
    thumbnail_file = download(thumbnail_url, destination=thumbnail_file_path)
    print('Thumbnail downloaded for ' + title)
    row['thumbnail_file'] = thumbnail_file_name

    # write thumbnail info to csv
    write_to_csv(video_list, headers)

    # download video and update video_list
    video_file = download(video_url, destination=video_file_path)
    print('Video downloaded for ' + title)
    row['video_file'] = video_file_name

    # write video info to csv
    write_to_csv(video_list, headers)


def download(url, destination):
    try:
        downloaded_file = urllib.request.urlretrieve(url, destination)
    except Exception as error:
        print(error)
        error_log.append(error)
        return ''
    else:
        return downloaded_file


def write_to_csv(video_list, headers):
    output_csv_file = config['csv_file_path']
    try:
        with open(output_csv_file, 'w', encoding='utf-8') as f2:
            writer = csv.DictWriter(f2, fieldnames=headers)
            writer.writeheader()
            writer.writerows(video_list)
    except Exception as error:
        print(error)
        error_log.append(error)


if __name__ == "__main__":
    main()
