import time
import controller
import logger as log
from configs import read_config as config


if __name__ == '__main__':
    # Performance counter timing parts
    tic = time.perf_counter()

    # read config
    config.read_config()

    # Log starting process
    log.logs_dir_check(config.setting['log_dir'])
    log.write_log('Split PDF process: Start')

    # Directory check
    controller.dir_check(config.setting['dest_dir'], config.setting['rcv_dir'])

    # Directory pdf file listing
    pdf_list = controller.dir_list(config.setting['data_dir'], config.setting['rcv_json_dir'])

    # If there are pdf file to split
    if len(pdf_list) > 0:

        # Read each pdf file that found in source directory
        for pdf in pdf_list:

            # Create file path
            pdf_path = '{}/{}'.format(config.setting['downloads_dir'], pdf)

            # Create PDF reader
            pdf_reader = controller.reader_pdf(pdf_path)

            # Count number of pdf page
            number_of_page = controller.count_page(pdf_reader)

            # Identify category each pdf file (invoice or packing list)
            pdf_group = controller.check_pdf_group(pdf_reader)

            # Can identify pdf group
            if pdf_group != 'can not define':

                # Get proforma invoice number of each page
                invoice_no_list = controller.get_invoice_list(number_of_page, pdf_reader, pdf_group)
                named_inv_list = controller.name_dupl_inv(invoice_no_list)

                # Initial value of split process status
                split_status = []
                # Split each of pdf file
                for page_no, page_inv_no in enumerate(named_inv_list):
                    # Initial value of each page spliting result
                    result = False

                    # Get a spliting page result
                    output_filename = controller.split_pdf(pdf_reader, pdf, page_no, pdf_group, page_inv_no
                                                             , config.setting['dest_dir'])

                    # Get file size in bytes
                    size = controller.file_size(output_filename, config.setting['dest_dir'])

                    # Add result to list
                    if output_filename != 'fail':
                        # Write to split data to SQL_DB
                        result = controller.write2sql(config.sql_db_conn_str
                                                      , output_filename
                                                      , pdf_group
                                                      , page_inv_no
                                                      , config.setting['taxno']
                                                      , size)

                    split_status.append(result)

                # All status in list is True (success splitting every pages)
                if False not in split_status:

                    # Log and Move source pdf file to success folder
                    log.write_log('Splitting process: Every page success')
                    controller.move_file(pdf, config.setting['downloads_dir'], config.setting['success_dir'])

                # One of status in list is False (one of pages fail to splitting)
                else:
                    # Crete error message
                    error_msg = 'Can not convert {} page:'.format(pdf)
                    for page_no, status in enumerate(split_status):
                        # collect page index that fail to splitting
                        if status is False:
                            error_msg += ' {},'.format(page_no+1)

                    # Log and ove source pdf file to fail folder
                    log.write_log('Splitting process: {}'.format(error_msg))
                    controller.move_file(pdf, config.setting['downloads_dir'], config.setting['fail_dir'])

            # Can NOT identify pdf group
            else:
                # Create error message
                error_msg = 'Can not identify {} category'.format(pdf)

                # Move source pdf file to fail folder
                controller.move_file(pdf, config.setting['downloads_dir'], config.setting['fail_dir'])

    # If there is NO pdf file to split
    else:
        log.write_log('Directory exploring: There is no pdf file to split')

    # Performance counter timing parts
    toc = time.perf_counter()
    log.write_log(f'Split PDF process: End in {toc - tic:0.4f} seconds')
