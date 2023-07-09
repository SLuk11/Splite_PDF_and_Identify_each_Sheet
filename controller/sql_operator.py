import sqlalchemy
import uuid
import logger as log

def create_batch_id():
    return uuid.uuid4()

def write2sql(connection_string, output_filename, pdf_group, page_inv_no, taxno, size):
    try:
        # Prepare data to write
        origin_name = '{}_PF{}'.format(pdf_group, page_inv_no)
        proforma_inv_no = page_inv_no.split('_')[0]

        # execute sql stored procedure
        engine = sqlalchemy.create_engine(connection_string)
        connection = engine.raw_connection()
        cursor = connection.cursor()
        cursor.execute("SP_DuplCheck ?, ?, ?, ?, ?, ?, ?"
                       , [origin_name, output_filename, pdf_group, proforma_inv_no, taxno, 'PDF', size])
        cursor.commit()

        log.write_log('Insert {} detail to SQL DB process: Done'.format(output_filename))
        return True

    except Exception as e:
        log.write_log('Insert {} detail to SQL DB process: {}'.format(output_filename, e.args[0]))
        return False

    finally:
        # Dispose of the engine
        cursor.close()
        connection.close()
        engine.dispose()
