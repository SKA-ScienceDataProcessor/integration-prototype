# Tango MySQL Docker image.

* Based on <https://github.com/tango-controls/docker-mysql>
* Updated SQL scripts to populate the database from those
  found in the `cppserver/database` folder in `tango-9.2.2.tar.gz` found
  at <http://downloads.sourceforge.net/project/tango-cs>

Build with:

```bash
docker build -t skasip/tango_mysql:test .
```

Run with:

```bash
docker run [-d] -e MYSQL_ROOT_PASSWORD=secret skasip/tango_mysql
```
