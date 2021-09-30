from pathlib import Path
import os
import time
DRY_RUN = False

HADOOP_HOME = "/usr/local/hadoop"
CMD_OFF_FIREWALL = """
firewall-cmd --state
systemctl stop firewalld.service
systemctl disable firewalld.service
firewall-cmd --state
"""


def copy_remote2local(
    password, ip, r_path, l_path,
):
    cmd = f"""sshpass -p '{password}' scp -o StrictHostKeyChecking=no root@{ip}:{r_path} {l_path}
    """

    print(cmd)
    if not DRY_RUN:
        return os.system(cmd)


def copy_local2remote(
    password, ip, l_path, r_path,
):
    cmd = f"""sshpass -p '{password}' scp -o StrictHostKeyChecking=no  {l_path} root@{ip}:{r_path}
    """
    print(cmd)
    if not DRY_RUN:
        return os.system(cmd)


def run_remote_cmd(password, ip, commands):
    cmd = f"""sshpass -p '{password}' ssh -t -o StrictHostKeyChecking=no root@{ip} 'source /etc/profile; {commands}'
    """
    print(cmd)
    if not DRY_RUN:
        return os.system(cmd)


# Add hosts
def get_hostname(i, ipp):
    if i == 0:
        return "hadoop-master"
    else:
        return f"hadoop-slave{i}"


ipps = []
with open(Path("./machines.txt"), "r") as f:
    for line in f:
        ws = line.split(" ")
        ip = ws[0]
        password = ws[1][:-1]
        ipps.append((ip, password))


master = ipps[0]
slaves = ipps[1:]

# Init SSH Keys
for ip, password in ipps:
    run_remote_cmd(password, ip, "rm -rf .ssh")
    copy_local2remote(password, ip, "~/.ssh/id_rsa.pub", "~/")
    copy_local2remote(password, ip, "./run_ssh.sh", "~/")
    run_remote_cmd(password, ip, "bash run_ssh.sh")
    copy_remote2local(password, ip, "~/.ssh/id_rsa.pub ", f"./pubs/{ip}.id_rsa.pub")


# SSH Login
for ip, password in slaves:
    # Copy master public key to slaves
    copy_local2remote(password, ip, f"./pubs/{master[0]}.id_rsa.pub", "~/")
    run_remote_cmd(
        password, ip, f"cat ~/{master[0]}.id_rsa.pub >> ~/.ssh/authorized_keys"
    )

    # Copy slaves public kyes to master
    copy_local2remote(master[1], master[0], f"./pubs/{ip}.id_rsa.pub", "~/")
    run_remote_cmd(
        master[1], master[0], f"cat ~/{ip}.id_rsa.pub >> ~/.ssh/authorized_keys"
    )


cmd = "".join(
    [
        f'echo "{ipp[0]} {get_hostname(i, ipp)}" >> /etc/hosts;'
        for i, ipp in enumerate(ipps)
    ]
)


# Install Java 8 , turn off firewall & disable SELINUX
for ip, password in ipps:
    run_remote_cmd(password, ip, cmd)
    copy_local2remote(password, ip, "./install_java8.sh", "~/")
    run_remote_cmd(password, ip, "bash install_java8.sh")
    copy_local2remote(password, ip, "./selinux", "/etc/selinux/config")
    run_remote_cmd(password, ip, CMD_OFF_FIREWALL)
    run_remote_cmd(password, ip, "shutdown -r now")

print("Wait 10 secs for server reboot.")
time.sleep(10)

ip_m, password_m = master
# Install Hadoop 3.3.1

print("Install Hadoop 3.3.1")

copy_local2remote(password_m, ip_m, "./install_hadoop.sh", "~/")
run_remote_cmd(password_m, ip_m, "bash install_hadoop.sh")


print("Add config for Hadoop 3.3.1")
for fn in ["core-site.xml", "hdfs-site.xml", "mapred-site.xml", "yarn-site.xml"]:
    copy_local2remote(password_m, ip_m, f"./{fn}", f"{HADOOP_HOME}/etc/hadoop/{fn}")


sub_cmd = ";".join(
    [
        f'echo "{get_hostname(i+1, ipp)}" >> {HADOOP_HOME}/etc/hadoop/workers'
        for i, ipp in enumerate(slaves)
    ]
)

cmd = f"""cd $HADOOP_HOME;
echo 'JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk' >> {HADOOP_HOME}/etc/hadoop/hadoop-env.sh;
mkdir {HADOOP_HOME}/tmp;
mkdir {HADOOP_HOME}/hdfs;
mkdir {HADOOP_HOME}/hdfs/name;
mkdir {HADOOP_HOME}/hdfs/data;
echo "hadoop-master" >> {HADOOP_HOME}/etc/hadoop/masters;
{sub_cmd}
"""
run_remote_cmd(password_m, ip_m, cmd)


# Copy hadoop and its conf files to slaves
sub_cmd2 = ";".join(
    [
        f"scp -o StrictHostKeyChecking=no -r /usr/local/hadoop {get_hostname(i+1, ipp)}:/usr/local/"
        for i, ipp in enumerate(slaves)
    ]
)
run_remote_cmd(password_m, ip_m, sub_cmd2)


# Delete workers on slave
for ip, password in slaves:
    run_remote_cmd(password, ip, "rm -rf /usr/local/hadoop/etc/hadoop/workers")

# Init hdfs
run_remote_cmd(password_m, ip_m, "hdfs namenode -format test_cluster")

