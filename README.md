# Automatic Hadoop Cluster Installation Script

OS: CentOS 8 (x64)
Hadoop : 3.3.1
Java: 8

## Usage

Add multiple (>=2) server info into a file named `machines.txt` like this:

```
192.168.1.2 password1
192.168.1.3 password1
...
```

In each line, the first column is the server IP while the second column is its root user password.


run:
```
python main.py
```

### Launch the cluster

Log into the master (first line in `machines.txt`) and run: 

```
$HADOOP_HOME/sbin/start-dfs.sh
$HADOOP_HOME/sbin/start-yarn.sh
mapred --daemon start historyserver
```

HDFS then will available on `192.168.1.2:9000`.

Stop the cluster:

```
$HADOOP_HOME/sbin/stop-dfs.sh
$HADOOP_HOME/sbin/stop-yarn.sh
mapred --daemon stop historyserver
```

