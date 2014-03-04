% Database Server
host = '156.145.113.86:3306';

% Database Username/Password
user = 'steffejr'; password = 'ticabl';

% Database Name

dbName = 'cnsdivdb'; 


% JDBC Parameters
jdbcString = sprintf('jdbc:mysql://%s/%s', host, dbName);

jdbcDriver = 'com.mysql.jdbc.Driver';
% Set this to the path to your MySQL Connector/J JAR

javaaddpath('/share/users/js2746_Jason/Scripts/mysql-connector-java-5.1.21')



% Create the database connection object dbConn = database(dbName, user , password, jdbcDriver, jdbcString);
dbConn = database(dbName, user , password, jdbcDriver, jdbcString);

isconnection(dbConn)

sqlcommand = 'select subid,visitid,StudyName from cnsdivdb.AllData where StudyName = ''CogRes'''

result = get(fetch(exec(dbConn,sqlcommand)))

