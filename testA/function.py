import logging

log = logging.getLogger("Brain")
log_handler = logging.StreamHandler()
log_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_format)
log.addHandler(log_handler)
log.setLevel(logging.INFO)

def lambda_handler(event, context):
    log.info( event )
    log.info( context )
    log.info("test2")
    return {
        'statusCode': 200,
        'body': "OK",
        'headers': {
            'Content-Type': 'application/json',
        }
    }

