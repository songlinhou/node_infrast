# Storage Modual
#### By Ray

-------

## 1.Introduction:

This modual provides APIs to interact with a central data storage service named LeanCloud (https://leancloud.cn/).

The APIs provides support for upper-layered moduals, mostly in the communication modual.

The credentials are stored in a json file called 'credential.json', which is necessary to interact with the storage service.

## 2.APIs

* *LeanCloud.lean_cloud_get( )*

For basic data query. ObjectID can be used to query a single record and the range queries with conditions are also supported.

* *lean_cloud_post( )*

For data creation. Invoking this function will insert a new record in a table. Duplicated records can exist in one table.

* *lean_cloud_put( )*

For data record update. It can update an existing record in the target table.

* *lean_cloud_delete( )*

Delete a record using ObjectID. This method can only delete one record at a time.



## 3.References

The basic usage of LeanCloud can be found at https://leancloud.cn/dashboard/apionline/index.html




