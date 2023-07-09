import os
import datetime
import logger as log
from PyPDF2 import PdfReader, PdfWriter


def reader_pdf(pdf_file_path):
    log.write_log('Create reader for {} : Done'.format(pdf_file_path))
    return PdfReader(pdf_file_path)

def count_page(pdf_reader):
    return len(pdf_reader.pages)

def check_pdf_group(pdf_reader):
    try:
        # Get first page text
        first_page = pdf_reader.pages[0]
        page_text = first_page.extract_text()

        # Check that page contains which pdf group's keyword
        if 'packing list' in page_text.lower():
            pdf_group = 'PK'

        elif 'p r o f o r m a' in page_text.lower():
            pdf_group = 'INV'

        else:
            pdf_group = 'can not define'

        log.write_log('check_pdf_group: define as {} group'.format(pdf_group))
        return pdf_group

    except Exception as e:
        log.write_log('check_pdf_group: {}'.format(e.args[0]))
        return 'can not define'

def extract_inv_no(pdf_reader, page_no, pdf_group):
    try:
        # Find keyword for proforma invoice search
        match pdf_group:
            case 'INV':
                search_keyword = 'proforma invoice:'
            case 'PK':
                search_keyword = 'proforma invoice number:'

        # Get text of whole page
        read_page = pdf_reader.pages[page_no]
        page_text = read_page.extract_text()

        # Split text into sentences for each line
        line_sentences = page_text.split('\n')

        # initial value for pf_inv_no
        pf_inv_no = None

        # inspect each line
        for stmt in line_sentences:

            # Check that line contain keyword or not?
            if search_keyword in stmt.lower():

                # Split sentences into words
                for word in stmt.split(':'):

                    # Get on invoice number
                    if 'proforma invoice' not in word.lower():
                        pf_inv_no = word

        log.write_log('extract_inv_no page {} : Done'.format(page_no+1))
        return pf_inv_no

    except Exception as e:
        log.write_log('extract_inv_no page {} : {}'.format(page_no+1, e.args[0]))
        # If can NOT detect invoice in pdf sheet return None
        return None

def extract_invpage_set(pdf_reader, page_no):
    try:
        # Get text of whole page
        read_page = pdf_reader.pages[page_no]
        page_text = read_page.extract_text()

        # Split text into sentences for each line
        line_sentences = page_text.split('\n')

        # inspect each line
        for stmt in line_sentences:

            # Check that line contain keyword or not?
            if 'page' in stmt.lower():
                inv_set_no = int(stmt.split(' ')[-1])

        return inv_set_no

    except Exception as e:
        log.write_log('extract_inv_set_no: {}'.format(e.args[0]))
        return 0


def get_invoice_list(number_of_page, pdf_reader, pdf_group):
    try:
        # Initial value of inv_list
        inv_list = []

        # Collect proforma invoice of each page to list (read page from back to front)
        for page_no in reversed(range(number_of_page)):

            # Get a proforma invoice of each page
            page_inv = extract_inv_no(pdf_reader, page_no, pdf_group)

            # If can NOT get an invoice number
            if page_inv is None:

                # Check is this page are in invoice's sub-page (some inv document longer than 1 page)
                page_set_no = extract_invpage_set(pdf_reader, page_no)

                # If it in sub-page
                if page_set_no > 1:
                    # use invoice number same as main-page (use inv no. that extracted before this page)
                    inv_list.append(inv_list[-1])

                # If it NOT in sub-page
                else:
                    # Can not specify invoice number of this page
                    inv_list.append('can_not_get_inv_no')

            # Can get an invoice number
            else:
                # Add invoice number to list
                inv_list.append(page_inv)

        # inverse list to normal sequence (read front to back)
        inv_list.reverse()

        log.write_log('get_invoice_list: Done')
        return inv_list

    except Exception as e:
        log.write_log('get_invoice_list: {}'.format(e.args[0]))
        # If can NOT create invoice number list return empty list
        return []

def name_dupl_inv(inv_list):
    try:
        unique_inv = set(inv_list)
        for x in unique_inv:
            if x != 'can_not_get_inv_no':
                number = 0
                for i in range(0, len(inv_list)):
                    if inv_list[i] == x:
                        if number >= 1:
                            inv_list[i] += '_B{}'.format(number)
                        number += 1

        return inv_list

    except Exception as e:
        log.write_log('name_dupl_inv: {}'.format(e.args[0]))
        # If can NOT create invoice number list return empty list
        return []


def split_pdf(pdf_reader, file_name, page_no, pdf_group, page_inv_no, save_dir):
    try:
        # Add page that going to write
        pdf_writer = PdfWriter()
        pdf_writer.add_page(pdf_reader.pages[page_no])

        # if this page has proforma invoice no.
        if page_inv_no != 'can_not_get_inv_no':

            # Create save name of this page
            now = datetime.datetime.now()
            now_format = now.strftime("%Y%m%d%H%M%S")
            output_filename = '{}_PF{}_{}.pdf'.format(pdf_group, page_inv_no, now_format)

            # Create saving file path
            complete_name = os.path.join(save_dir, output_filename)

            # save pdf file to directory
            with open(complete_name, "wb") as output_pdf:
                pdf_writer.write(output_pdf)

            log.write_log('split_pdf: {} Done'.format(output_filename))
            # After complete splitting process return process result as True
            return output_filename

        # if this page dose NOT has proforma invoice no.
        else:
            # Create fail name of this page
            fail_name = '{}_file_{}_page_{}_non_PFno.pdf'.format(pdf_group, file_name.split(".")[0], page_no)

            # Create saving file path
            complete_name = os.path.join(save_dir, fail_name)

            # save pdf file to directory
            with open(complete_name, "wb") as output_pdf:
                pdf_writer.write(output_pdf)

            log.write_log('split_pdf: Fail')
            # Not complete all splitting process (can NOT specific inv_no), so return splitting resul as False
            return 'fail'

    except Exception as e:
        log.write_log('split_pdf: {}'.format(e.args[0]))
        # Return splitting resul as False
        return 'fail'
