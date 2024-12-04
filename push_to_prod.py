import boto3
import boto3.session
import argparse

# argparse
parser = argparse.ArgumentParser(description='Push a Lambda zip file from DEV to PROD')
parser.add_argument('--dev_bucket', type=str, help='The DEV bucket name', required=True)
parser.add_argument('--prod_bucket', type=str, help='The PROD bucket name', required=True)
parser.add_argument('--key', type=str, help='The key of the object to push', required=True)
parser.add_argument('--user', type=str, help='The user pushing the object', required=True)
parser.add_argument('--dev_profile', type=str, help='The AWS profile for the DEV stack. Default: Brain-DEV', default='Brain-DEV')
parser.add_argument('--prod_profile', type=str, help='The AWS profile for the PROD stack. Default: Brain-PROD', default='Brain-PROD')
parser.add_argument('--version_file', type=str, help='The file containing the version number', default='.VERSION')
args = parser.parse_args()

DEV_PROFILE = args.dev_profile
PROD_PROFILE = args.prod_profile

with open( args.version_file, 'r' ) as f:
    VERSION = f.read().strip()

print( f"Pushing version: {VERSION}" )

# ETag is a hash of the object in the DEV stack
def get_dev_s3_object_metadata_and_etag(dev_bucket, key):
    my_session = boto3.session.Session( profile_name = DEV_PROFILE )
    s3 = my_session.client( 's3' )
    
    obj = s3.head_object(
        Bucket  = dev_bucket, 
        Key     = key
    )
    metadata = obj['Metadata']
    etag = obj['ETag']
    return metadata, etag

# Get the object
def get_dev_s3_object(dev_bucket, key):
    my_session = boto3.session.Session( profile_name = DEV_PROFILE )
    s3 = my_session.client( 's3' )
    return s3.get_object(
        Bucket  = dev_bucket, 
        Key     = key
    )

# ETag is a hash of the object in the PROD stack
def get_prod_s3_object_metadata_and_etag(prod_bucket, key):
    my_session = boto3.session.Session( profile_name = PROD_PROFILE )
    s3 = my_session.client( 's3' )
    
    obj = s3.head_object(
        Bucket  = prod_bucket, 
        Key     = key
    )
    metadata = obj['Metadata']
    etag = obj['ETag']
    return metadata, etag

def upload_to_prod( prod_bucket, key, object, metadata ):
    my_session = boto3.session.Session( profile_name = PROD_PROFILE )
    s3 = my_session.client( 's3' )
    
    # Upload the object
    s3.put_object(
        Bucket      = prod_bucket,
        Key         = key,
        Body        = object['Body'].read(),
        Metadata    = metadata
    )

def push_to_prod( prod_bucket, dev_bucket, key, current_user ):
    dev_version_key = f"{key}.{VERSION}.zip"
    key = f"{key}.zip"
    old_metadata, old_etag = get_prod_s3_object_metadata_and_etag( prod_bucket=prod_bucket, key=key )
    pushed_by = "unknown"
    if( 'pushed_by' in old_metadata ):
        pushed_by = old_metadata['pushed_by']
    print( f"Current PROD version: {old_metadata['version']} with ETag: {old_etag} built by: {old_metadata['builder']} pushed by: {pushed_by}" )

    dev_metadata, dev_etag = get_dev_s3_object_metadata_and_etag( dev_bucket=dev_bucket, key=dev_version_key )
    object = get_dev_s3_object( dev_bucket=dev_bucket, key=dev_version_key )
    new_metadata = {
        'version': dev_metadata['version'],
        'builder': dev_metadata['builder'],
        'pushed_by': current_user
    }
    print( f"New DEV version: {dev_metadata['version']} with ETag: {dev_etag} built by: {dev_metadata['builder']} will be pushed by {new_metadata['pushed_by']}" )

    upload_to_prod( prod_bucket=prod_bucket, key=key, object=object, metadata=new_metadata )

    check_metadata, check_etag = get_prod_s3_object_metadata_and_etag( prod_bucket=prod_bucket, key=key )
    
    print( f"New PROD version: {check_metadata['version']} with ETag: {check_etag} built by: {check_metadata['builder']} pushed by: {check_metadata['pushed_by']}" )

    if( dev_etag != check_etag ):
        print( f"\n\nETag mismatch: {key} DEV: {dev_etag} PROD: {check_etag}\n\n" )
        raise Exception( f"ETag mismatch: {key} DEV: {dev_etag} PROD: {check_etag}" )
    else:        
        print( f"ETag match: DEV: {dev_etag} PROD: {check_etag}" )
    
push_to_prod( 
    dev_bucket  = args.dev_bucket,
    key         = args.key,
    prod_bucket = args.prod_bucket,
    current_user= args.user      
)