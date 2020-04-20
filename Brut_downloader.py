import urllib.request
import csv

environment = {
    'cloud-drive': {
        'csv_file_path': '/Users/Lazybeam/Desktop/Work/MCP/Brut/download.csv',
        'thumbnail_download_dir': '/Users/Lazybeam/Dropbox/Media Content Provider/Brut/For Editors/thumbnails/',
        'video_download_dir': '/Users/Lazybeam/Dropbox/Media Content Provider/Brut/For Editors/videos/'
    },
    'local': {
        'csv_file_path': '/Users/Lazybeam/Desktop/Work/MCP/Brut/download.csv',
        'thumbnail_download_dir': '/Users/Lazybeam/Desktop/Work/Brut/output/thumbnails/',
        'video_download_dir': '/Users/Lazybeam/Desktop/Work/Brut/output/videos/'
    }

}

error_log = []

# switch if cloud drive is full
config = environment['cloud-drive']


def main():

    # video_list holds all info
    video_list = []
    headers = load_csv((config['csv_file_path']), video_list)

    # for each item in video_list, download thumbnail and video and write to csv
    download_assets(video_list, headers)

    if not error_log:
        print('\n---------END-----------')
        print('Successfully downloaded assets')
    else:
        print('\n---------END-----------')
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
    category = row['category']

    thumbnail_url = row['thumbnail_url']
    video_url = row['video_url']

    print(title)

    media_id = video_url.split('video/')[1][0:8]

    string = category + '-' + media_id

    # set destination path
    thumbnail_file_name = string + '.jpg'
    video_file_name = string + '.mp4'

    thumbnail_file_path = config['thumbnail_download_dir'] + thumbnail_file_name
    video_file_path = config['video_download_dir'] + video_file_name

    # download thumbnail and update video_list
    thumbnail_file = download(thumbnail_url, destination=thumbnail_file_path)
    if thumbnail_file != '':
        print('Thumbnail downloaded')
        row['thumbnail_file'] = thumbnail_file_name
    else:
        print('Failed to download thumbnail')

    # write thumbnail info to csv
    write_to_csv(video_list, headers)

    # download video and update video_list
    video_file = download(video_url, destination=video_file_path)
    if video_file != '':
        print('Video downloaded')
        row['video_file'] = video_file_name
    else:
        print('Failed to download video')

    # write video info to csv
    write_to_csv(video_list, headers)


def download(url, destination):

    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)

    try:
        downloaded_file = urllib.request.urlretrieve(url, destination)
        return downloaded_file
    except Exception as error:
        error_log.append(error)
        return ''


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
