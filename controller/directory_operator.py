import os
import json
import shutil
import logger as log

def move_file(file_name, source_dir, destination_dir):
    try:
        # Create file origin path and destination path
        origin = '{}/{}'.format(source_dir, file_name)
        target = '{}/{}'.format(destination_dir, file_name)

        # Move file
        shutil.move(origin, target)

        log.write_log('Move file {} to {}: Done'.format(file_name, destination_dir))
    except Exception as e:
        log.write_log('Move file {} to {}: {}'.format(file_name, destination_dir, e))


def dir_list(data_dir, rcv_json_dir):
    try:
        # list all json file in data directory
        files = os.listdir(data_dir)

        # loop to filter only 'pdf' prefix file
        json_list = []
        for file in files:
            # filter only .pdf file
            if str(file.lower()).startswith('pdf'):
                json_list.append(file)

        if len(json_list) > 0:
            pdf_list = []
            # loop thur each 'pdf' json file
            for file_name in json_list:

                # read json file
                json_file_fullpath = os.path.join(data_dir, file_name)
                with open(json_file_fullpath, "r") as f:
                    obj = json.load(f)

                    # loop each pdf file detail that contain in json object
                    for pdf_detail in obj:
                        # collect data from pdf detail data as list
                        pdf_list.append(pdf_detail['FileName'])

                # move json file after retrieve data
                move_file(file_name, data_dir, rcv_json_dir)

            log.write_log('Listing_file_process: Done')

            # Response result
            return pdf_list

        # If there is NO .pdf file return empty list
        else:
            log.write_log('Listing_file_process: Done')

            # Response result
            return []

    except Exception as e:
        log.write_log('Listing_file_process: {}'.format(e.args[0]))
        # If there is NO .pdf file return empty list
        return []


def dir_check(destination_dir, receive_dir):
    try:
        # Check if destination_dir folder exist or not, if not create a new one
        if not os.path.exists(destination_dir):
            os.mkdir(destination_dir)

        # Check if receive_dir folder exist or not, if not create a new one
        if not os.path.exists(receive_dir):
            os.mkdir(receive_dir)
            os.mkdir('{}/success'.format(receive_dir))
            os.mkdir('{}/fail'.format(receive_dir))
            os.mkdir('{}/json'.format(receive_dir))

        return True

    except Exception as e:
        log.write_log('Directory_check: {}'.format(e.args[0]))
        # If there is NO .pdf file return empty list
        return False


def file_size(file_name, directory):
    bytes_size = os.path.getsize('{}/{}'.format(directory, file_name))
    return bytes_size
