# Influx Database

The Modul calcdata.py m is built to collect information from mi scale and send it to InfluxDB. The eventual goal in creating this program was to provide body data metrics and alerts to Grafana.



## Prepare Database
```bash
$ influx
# Connected to http://localhost:8086 version 1.8.2
# InfluxDB shell version: 1.8.2
CREATE DATABASE historydata
...
exit
```

## Remove Measurment
```bash
# connect to influxdb
$ influx
show databases
use historydata
# Using database historydata
show measurements
drop measurement MISCALEDATA_USERNAME
....
exit
```

## Import previous scale data to the influxdb
```bash
$ cd tests
$ python3 updateInfluxdb.py
```



<br><hr>
## Information
- https://www.influxdata.com/blog/getting-started-python-influxdb/<br>
- https://github.com/influxdata/influxdb-python <br>
- https://github.com/influxdata/influxdb-python/blob/master/examples/tutorial_server_data.py<br>