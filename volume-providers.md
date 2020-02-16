```by professor's notes:
collect how each provider deals with volumes. Important is you include the links to
python api
REST api
manual
...
is there documentation about cost?
is there documentation on how to move volumes from one provider to the next
```

* AWS:

python api: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html

REST api: https://docs.aws.amazon.com/apigateway/api-reference/

Documentation about volume cost: https://aws.amazon.com/ebs/pricing/

manual: https://docs.aws.amazon.com/

* Google:

python api: https://cloud.google.com/sdk

REST api: https://cloud.google.com/apis/docs/overview

Documentation about volume cost: https://cloud.google.com/compute/disks-image-pricing

manual: https://cloud.google.com/docs

* Azure:

* OpenStack

* Documentation on how to move volumes from one provider to the next: 
    * from Amazon S3
        * Migrating from Amazon S3 to Cloud Storage
        
        https://cloud.google.com/storage/docs/migrating#storage-list-buckets-s3-python
        
        https://github.com/adzerk/s3-to-google-cloud-storage-connector
        
        * Migrating from Amazon S3 to Azure Blob Storage
        
        https://github.com/Azure-for-Startups/Amazon-S3-to-Azure-Storage-demo/blob/master/README.md
        
        * Migrating from Amazon S3 to OpenStack
        
    * from Cloud Storage
    
        * Migrating from Cloud Storage to Amazon S3
        
        https://www.quora.com/How-can-I-migrate-data-from-Google-cloud-storage-into-AWS-S3-buckets
        
        * Migrating from Cloud Storage to Azure Blob Storage
        
        https://blog.bitscry.com/2019/12/30/data-transfer-google-cloud-storage-to-azure-blob-storage/
        
        * Migrating from Cloud Storage to OpenStack
        
    * from Azure Blob Storage
        
        * Migrating from Azure Blob Storage to Amazon S3
        
        * Migrating from Azure Blob Storage to Cloud Storage
        
        * Migrating from Azure Blob Storage to OpenStack
        
    * from OpenStack