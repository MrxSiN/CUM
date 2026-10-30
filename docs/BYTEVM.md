# Generic QEMU isolation

`host/bytehost/qemu_isolation.py` is a generic alternative to the existing Docker
service. It transports opaque files and runs an explicit argument vector. It has
no language parser, transformation selector or CUM release decision. Native BF
continues to select workflow operations.

Each invocation verifies QEMU/qemu-img file pins and a standalone QCOW2 image
digest, creates a disposable copy-on-write overlay, and boots with `-nic none`.
There are no host filesystem shares, drive mappings, clipboard or guest-agent
commands. Input directories are copied through a framed virtio-serial channel;
the guest job runs under the declared nonroot UID/GID with no-new-privileges,
process/file-size limits and a timeout. Readonly inputs belong to guest root.
Only explicitly named regular files inside writable input directories can return.
The VM is killed after the response or any failure. The pinned image and QEMU
installation are trusted infrastructure; this does not establish resistance to
hypervisor vulnerabilities or hostile host administrators.

The image must be self-contained: qcow2 backing files and external data files are
rejected. Tool executable hashes do not inventory the complete QEMU installation.
Memory/CPU budgets describe the guest allocation, not all host overhead. TCG
timings are emulation measurements and cannot establish native runtime budgets.
The loopback control socket assumes trusted local host processes.

## Provision a separate tool image

Use an owner-controlled private directory. Obtain an official Ubuntu cloud image,
verify its signed checksum list against the independently checked Ubuntu cloud
signing-key fingerprint, and retain the original checksum/signature and image.
The executed base was Ubuntu 24.04.5, release 20261017, amd64 image SHA-256
`04e8f2461a16a44e78a370284471f29616cdd9baf1893df25807b71f985b6c94`.
The checksum signature validated with fingerprint
`D2EB44626FDDC30B513D5BB71A5D6C4C7DB87C81`.

Create a new NoCloud seed:

```powershell
python -m host.providers.bytevm_seed private/bytevm-seed
```

It installs only Python, OpenSSL, Wine and Git plus the generic guest agent.
Serve only that seed directory over a temporary loopback HTTP server. Provision
a fresh 16 GiB qcow2 overlay using QEMU user networking and the NoCloud SMBIOS
parameter `ds=nocloud-net;s=http://10.0.2.2:PORT/`. Supply no project or identity
directories during provisioning. Wait for `BYTEVM_PROVISIONED` and a clean poweroff;
then stop the seed server. Package repositories are mutable, so a newly provisioned
image has a new identity even when its base matches.

Flatten it into a new standalone disk with `qemu-img convert -O qcow2`, independently
hash it and the actual QEMU/qemu-img executables, and fill the ignored VM binding.
The validation runner supplies a DMI nonce and packet budget to the guest service.
The image disables cloud-init for validation boots; those boots have no NIC.
Never add recovery identities or original projects to the reusable image.

Official references: [Ubuntu cloud images](https://cloud-images.ubuntu.com/releases/noble/release/),
[image signatures](https://ubuntu.com/docs/public-images/public-images-reference/artifacts/),
[cloud signing key](https://wiki.ubuntu.com/Security/FAQ),
[NoCloud](https://docs.cloud-init.io/en/latest/reference/datasources/nocloud.html),
[QEMU system options](https://www.qemu.org/docs/master/system/qemu-manpage.html).

## Bind a job and policy

`config/clean-recovery-qemu.example.json` and its policy example contain deliberate
invalid pins. Bind exact clone/runtime/identity/trust/binding directories plus an
empty result directory. The independently approved policy stays outside every
mount and pins the complete mount set, readonly inventories, image/VM identities,
arguments, environment and returned destinations. For Wine, give the nonroot job
an owned `HOME` and `WINEPREFIX` in its writable directory. Keep original, snapshot
and reference roots forbidden. No recovery identity belongs in a build job.

The existing clean-recovery binding must pin the real guest OpenSSL binary and
Wine launcher, use guest paths, and write result/scope/receipt/flow files named by
the output allowlist. Execute it through generic service 44. Validate its receipt,
safely extract the returned archive and compare the retained scope separately.
The synthetic tests exercise these boundaries; they do not approve a real release.

Export the reviewed public clone files without `.git` metadata before mounting
them for recovery, then inventory that complete export. Recovery does not need
Git hooks, configuration or object history. The real clone/audit remains a separate
step. Large responses use complete-write framing; a nonce-bound READY packet must
arrive before sending a job, and host deadlines cover the complete response.

Enable the real VM tests with `BYTEHOST_VM_TESTS=1` and `BYTEHOST_VM_BINDING` pointing
to the ignored, independently pinned binding. Native compiler and signed recovery
tests additionally require their documented native/crypto opt-ins. The build VM
receives no identities; recovery receives no original or reference trees.

Complete offline runtime backup, dependency provenance review and a cold restore
on a different host are separate requirements. A locally retained VM disk alone
does not prove those requirements.
