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

    python api: 
    
    boto3:
    
    <https://boto3.amazonaws.com/v1/documentation/api/latest/index.html>
    
        * EC2 volume:
            
            <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#volume>
    
    REST api: 
    
    <https://docs.aws.amazon.com/apigateway/api-reference/>
    
    Documentation about volume cost: 
    
    <https://aws.amazon.com/ebs/pricing/>
    
    <https://medium.com/@stefanroman/calculate-price-of-ebs-volumes-with-python-76687bb24530>
    
    manual: 
    
    <https://docs.aws.amazon.com/>
    
    * about S3 duplication, maybe use it as migrate between and within regions:
    
         <https://aws.amazon.com/s3/features/replication/#Amazon_S3_Cross-Region_Replication_.28CRR.29>
    
    * Storage services:
    
         <https://www.missioncloud.com/blog/resource-amazon-ebs-vs-efs-vs-s3-picking-the-best-aws-storage-option-for-your-business>
    
    EBS:
    
    EFS:
    
    S3:

* Google:

    python api: 
    
    <https://cloud.google.com/sdk>
    
    <https://github.com/googleapis/google-cloud-python#google-cloud-python-client>
    
    REST api: 
    
    <https://cloud.google.com/apis/docs/overview>
    
    Documentation about volume cost: 
    
    <https://cloud.google.com/compute/disks-image-pricing>
    
    manual: 
    
    <https://cloud.google.com/docs>
    
    * command about gcloud disk (volume):
        
         <https://cloud.google.com/s/results?q=disk>

* Azure:

* OpenStack

* Documentation on how to move volumes from one provider to the next: 
    * from Amazon S3
        * Migrating from Amazon S3 to Cloud Storage
        
        <https://cloud.google.com/storage/docs/migrating#storage-list-buckets-s3-python>
        
        <https://github.com/adzerk/s3-to-google-cloud-storage-connector>
        
        * Migrating from Amazon S3 to Azure Blob Storage
        
        <https://github.com/Azure-for-Startups/Amazon-S3-to-Azure-Storage-demo/blob/master/README.md>
        
        * Migrating from Amazon S3 to OpenStack
        
    * from Cloud Storage
    
        * Migrating from Cloud Storage to Amazon S3
        
        <https://www.quora.com/How-can-I-migrate-data-from-Google-cloud-storage-into-AWS-S3-buckets>
        
        * Migrating from Cloud Storage to Azure Blob Storage
        
        <https://blog.bitscry.com/2019/12/30/data-transfer-google-cloud-storage-to-azure-blob-storage/>
        
        * Migrating from Cloud Storage to OpenStack
        
    * from Azure Blob Storage
        
        * Migrating from Azure Blob Storage to Amazon S3
        
        * Migrating from Azure Blob Storage to Cloud Storage
        
        * Migrating from Azure Blob Storage to OpenStack
        
    * from OpenStack