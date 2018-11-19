USE tango_db;

#
# Create all database tables
#

source /scripts/create_db_tables.sql

#
# Load the stored procedures
#

source /scripts/stored_procedures.sql

#
# Init the history identifiers
#

CALL init_history_ids();

#
# Create entry for database device server in device table
#

DELETE FROM device WHERE server='DataBaseds/2';

INSERT INTO device VALUES ('sys/database/2',NULL,'sys','database','2',0,'nada','nada','DataBaseds/2',0,'DataBase','nada',0,0,'nada');
INSERT INTO device VALUES ('dserver/DataBaseds/2',NULL,'dserver','DataBaseds','2',0,'nada','nada','DataBaseds/2',0,'DServer','nada',0,0,'nada');

#
# Create entry for test device server in device table
#

DELETE FROM device WHERE server='TangoTest/test';

INSERT INTO device VALUES ('sys/tg_test/1',NULL,'sys','tg_test','1',0,'nada','nada','TangoTest/test',0,'TangoTest','nada',0,0,'nada');
INSERT INTO device VALUES ('dserver/TangoTest/test',NULL,'dserver','TangoTest','test',0,'nada','nada','TangoTest/test',0,'DServer','nada',0,0,'nada');

#
# Create entry for Tango Control Access in device table
#

DELETE FROM device WHERE server='TangoAccessControl/1';
DELETE FROM server WHERE name='tangoaccesscontrol/1';

INSERT INTO device VALUES ('sys/access_control/1',NULL,'sys','access_control','1',0,'nada','nada','TangoAccessControl/1',0,'TangoAccessControl','nada',0,0,'nada');
INSERT INTO device VALUES ('dserver/TangoAccessControl/1',NULL,'dserver','TangoAccessControl','1',0,'nada','nada','TangoAccessControl/1',0,'DServer','nada',0,0,'nada');
INSERT INTO server VALUES ('tangoaccesscontrol/1','',0,0);

#
# Create default user access
#

CALL tango_db.init_tac_tables();

#
# Create entries in the property_class tables for controlled access service
#

DELETE FROM property_class WHERE class='Database';

INSERT INTO property_class VALUES('Database','AllowedAccessCmd',1,'DbGetServerInfo',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',2,'DbGetServerNameList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',3,'DbGetInstanceNameList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',4,'DbGetDeviceServerClassList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',5,'DbGetDeviceList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',6,'DbGetDeviceDomainList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',7,'DbGetDeviceFamilyList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',8,'DbGetDeviceMemberList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',9,'DbGetClassList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',10,'DbGetDeviceAliasList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',11,'DbGetObjectList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',12,'DbGetPropertyList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',13,'DbGetProperty',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',14,'DbGetClassPropertyList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',15,'DbGetClassProperty',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',16,'DbGetDevicePropertyList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',17,'DbGetDeviceProperty',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',18,'DbGetClassAttributeList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',19,'DbGetDeviceAttributeProperty',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',20,'DbGetDeviceAttributeProperty2',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',21,'DbGetLoggingLevel',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',22,'DbGetAliasDevice',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',23,'DbGetClassForDevice',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',24,'DbGetClassInheritanceForDevice',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',25,'DbGetDataForServerCache',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',26,'DbInfo',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',27,'DbGetClassAttributeProperty',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',28,'DbGetClassAttributeProperty2',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',29,'DbMysqlSelect',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',30,'DbGetDeviceInfo',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',31,'DbGetDeviceWideList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',32,'DbImportEvent',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',33,'DbGetDeviceAlias',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',34,'DbGetCSDbServerList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',35,'DbGetDeviceClassList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',36,'DbGetDeviceExportedList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',37,'DbGetHostServerList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',38,'DbGetAttributeAlias2',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',39,'DbGetAliasAttribute',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',40,'DbGetClassPipeProperty',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',41,'DbGetDevicePipeProperty',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',42,'DbGetClassPipeList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',43,'DbGetDevicePipeList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',44,'DbGetAttributeAliasList',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('Database','AllowedAccessCmd',45,'DbGetForwardedAttributeListForDevice',NOW(),NOW(),NULL);

#
#
#

DELETE FROM property_class WHERE class='DServer';

INSERT INTO property_class VALUES('DServer','AllowedAccessCmd',1,'QueryClass',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('DServer','AllowedAccessCmd',2,'QueryDevice',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('DServer','AllowedAccessCmd',3,'EventSubscriptionChange',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('DServer','AllowedAccessCmd',4,'DevPollStatus',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('DServer','AllowedAccessCmd',5,'GetLoggingLevel',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('DServer','AllowedAccessCmd',6,'GetLoggingTarget',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('DServer','AllowedAccessCmd',7,'QueryWizardDevProperty',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('DServer','AllowedAccessCmd',8,'QueryWizardClassProperty',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('DServer','AllowedAccessCmd',9,'QuerySubDevice',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES('DServer','AllowedAccessCmd',10,'ZMQEventSubscriptionChange',NOW(),NOW(),NULL);

#
#
#

DELETE FROM property_class WHERE class='Starter';

INSERT INTO property_class VALUES ('Starter','AllowedAccessCmd',1,'DevReadLog',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES ('Starter','AllowedAccessCmd',2,'DevStart',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES ('Starter','AllowedAccessCmd',3,'DevGetRunningServers',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES ('Starter','AllowedAccessCmd',4,'DevGetStopServers',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES ('Starter','AllowedAccessCmd',5,'UpdateServerList',NOW(),NOW(),NULL);

#
#
#

DELETE FROM property_class WHERE class='TangoAccessControl';

INSERT INTO property_class VALUES ('TangoAccessControl','AllowedAccessCmd',1,'GetUsers',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES ('TangoAccessControl','AllowedAccessCmd',2,'GetAddressByUser',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES ('TangoAccessControl','AllowedAccessCmd',3,'GetDeviceByUser',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES ('TangoAccessControl','AllowedAccessCmd',4,'GetAccess',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES ('TangoAccessControl','AllowedAccessCmd',5,'GetAllowedCommands',NOW(),NOW(),NULL);
INSERT INTO property_class VALUES ('TangoAccessControl','AllowedAccessCmd',6,'GetAllowedCommandClassList',NOW(),NOW(),NULL);


