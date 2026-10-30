"""Write a NoCloud seed for a generic, secret-free ByteVM tool image."""
import argparse
import json
from pathlib import Path


def seed(destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    service = ("[Unit]\nDescription=Opaque one-job VM transport\nAfter=local-fs.target\n"
               "[Service]\nType=simple\nExecStart=/usr/bin/python3 /opt/bytevm/bytevm_agent.py\n"
               "[Install]\nWantedBy=multi-user.target\n")
    config = {"package_update": True, "apt": {"conf": 'APT::Install-Recommends "false";\nAPT::Install-Suggests "false";'},
              "packages": ["python3", "openssl", "wine64", "git"],
              "write_files": [{"path": "/opt/bytevm/bytevm_agent.py", "permissions": "0700",
                               "content": Path(__file__).with_name("bytevm_agent.py").read_text()},
                              {"path": "/etc/systemd/system/bytevm-agent.service", "permissions": "0644", "content": service}],
              "runcmd": [["systemctl", "enable", "bytevm-agent.service"],
                         ["systemctl", "disable", "ssh.service", "ssh.socket"],
                         ["touch", "/etc/cloud/cloud-init.disabled"],
                         ["sh", "-c", "python3 --version && openssl version && /usr/lib/wine/wine64 --version && git --version && echo BYTEVM_PROVISIONED"]],
              "power_state": {"mode": "poweroff", "delay": "now", "timeout": 60, "condition": True}}
    (destination / "user-data").write_text("#cloud-config\n" + json.dumps(config), encoding="utf-8")
    (destination / "meta-data").write_text("instance-id: bytevm-provision\nlocal-hostname: bytevm\n", encoding="utf-8")
    (destination / "network-config").write_text("version: 2\nethernets:\n  ens3:\n    dhcp4: true\n", encoding="utf-8")
    (destination / "vendor-data").write_bytes(b"")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination")
    seed(parser.parse_args().destination)
