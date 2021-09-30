
echo 'export HADOOP_HOME=/usr/local/hadoop' >> /etc/profile
echo 'export PATH=$PATH:$HADOOP_HOME/bin' >> /etc/profile

echo 'export HDFS_NAMENODE_USER="root"' >> /etc/profile
echo 'export HDFS_DATANODE_USER="root"' >> /etc/profile
echo 'export HDFS_SECONDARYNAMENODE_USER="root"' >> /etc/profile
echo 'export YARN_RESOURCEMANAGER_USER="root"' >> /etc/profile
echo 'export YARN_NODEMANAGER_USER="root"' >> /etc/profile


echo 'export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk' >> /etc/profile
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> /etc/profile

yum install -y java-1.8.0-openjdk*

source /etc/profile