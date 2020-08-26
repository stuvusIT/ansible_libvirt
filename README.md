# libvirt

This role installs [libvirt](https://libvirt.org/) and can define domains.
It is intended to only use the `qemu://system` daemon.

## Requirements
 - Debian

## Manual post configuration
 - If using libvirt commands without sudo is desired
   - Make sure `/etc/profile.d/libvirt_default_uri.sh` is being sourced by /etc/profile
   - Admin users must be in the groups `libvirt`, `libvirt-qemu` and `kvm`

## Role Variables

| Name                            |           Required/Default            | Description                                                                                                                                      |
| ------------------------------- | :-----------------------------------: | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `libvirt_script_src_dir`        | `/usr/local/src/libvirt_ansible_role` | The directory where the role places the scripts needed by the role.                                                                              |
| `libvirt_configuration_dir`     |      `/etc/libvirt_ansible_role`      | The directory where the role places some configuration files.                                                                                    |
| `libvirt_domain_definition_dir` |  `/etc/libvirt_ansible_role/domains`  | The directory where the role places the definitions for the domains before loading them into libvirt as well as the extra files for each domain. |
| `libvirt_domains`               |                 `[]`                  | A list of domains to define. Each entry in the list should be a [DomainDict](#domain-dict).                                                      |


## Domain dict
Each domain is defined by a dict with following keys:
| Name          | Required/Default | Description                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ------------- | :--------------: | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `definition`  |     required     | The definition of the domain. This must have the [Xml description format](#xml-description-format) as it will be converted to xml. The contents of the xml must be according to the [libvirt domain xml format](https://libvirt.org/formatdomain.html)                                                                                                                                                                        |
| `extra_files` |       `[]`       | A list of files to be put on the hypervisor in the subdirectory of `libvirt_domain_definition_dir` for this domain. Each item should be a dict containing the keys and values as expected by the [copy module](https://docs.ansible.com/ansible/latest/modules/copy_module.html). The value of [dest](https://docs.ansible.com/ansible/latest/modules/copy_module.html) will be prepended with the above mentioned directory. |

For the role to properly process the domain, the [name element](https://libvirt.org/formatdomain.html#general-metadata) must exist and have content. This name should be unique.

## Xml description format
With this format it is possible to describe an xml document in json/yaml.
Each xml element is a dict with these keys:

| Name    | Required/Default |                  Type                  | Description                                                                                                   |
| ------- | :--------------: | :------------------------------------: | ------------------------------------------------------------------------------------------------------------- |
| name    |     required     |                 string                 | The name of the xml element                                                                                   |
| attrs   |     optional     |        dict, with string values        | The attributes of the xml element                                                                             |
| content |     optional     | string, number or list of xml elements | The string in the element (number is converted to string) or a list of xml elements contained inside this one |


## Example

```yml
libvirt_domains:
  - extra_files:
      - dest: initialInstallationArgs.txt
        content: |
          expectedRootDiskAt=/storage/vms/mydomain.qcow2
          initialIpAddr=192.168.10.107
      - dest: foo
        content: bar
        mode: 600
    definition:
      name: domain
      attrs:
        type: kvm
      content:
        - name: name
          content: MyDomain
        - name: uuid
          content: a373ac44-5a2f-45af-8b87-39055d069f65
        - name: metadata
          content:
            - name: libosinfo:libosinfo
              attrs:
                xmlns:libosinfo: http://libosinfo.org/xmlns/libvirt/domain/1.0
              content:
                - name: libosinfo:os
                  attrs:
                    id: http://debian.org/debian/10
        - name: memory
          content: 4194304
        - name: currentMemory
          content: 4194304
        - name: vcpu
          content: 1
        - name: os
          content:
            - name: type
              attrs:
                arch: x86_64
                machine: q35
              content: hvm
            - name: boot
              attrs:
                dev: hd
        - name: features
          content:
            - name: acpi
            - name: apic
        - name: cpu
          attrs:
            mode: host-model
        - name: clock
          attrs:
            offset: utc
          content:
            - name: timer
              attrs:
                name: rtc
                tickpolicy: catchup
            - name: timer
              attrs:
                name: pit
                tickpolicy: delay
            - name: timer
              attrs:
                name: hpet
                present: 'no'
        - name: pm
          content:
            - name: suspend-to-mem
              attrs: 
                enabled: 'no'
            - name: suspend-to-disk
              attrs:
                enabled: 'no'
        - name: devices
          content:
            - name: emulator
              content: /usr/bin/qemu-system-x86_64
            - name: disk
              attrs:
                type: file
                device: disk
              content:
                - name: driver
                  attrs:
                    name: qemu
                    type: qcow2
                - name: source
                  attrs:
                    file: /storage/vms/mydomain.qcow2
                - name: target
                  attrs:
                    dev: vda
                    bus: virtio
            - name: disk
              attrs:
                type: file
                device: cdrom
              content:
                - name: driver
                  attrs: 
                    name: qemu
                    type: raw
                - name: source
                  attrs:
                    file: /storage/isos/debian-10.4.0-amd64-netinst.iso
                - name: target
                  attrs:
                    dev: sda
                    bus: sata
                - name: readonly
            - name: controller
              attrs:
                type: usb
                index: 0
                model: qemu-xhci
                ports: 15
            - name: interface
              attrs:
                type: bridge
              content:
                - name: source
                  attrs:
                    bridge: br0
                - name: mac
                  attrs:
                    address: 52:54:00:e1:61:fd
                - name: model
                  attrs:
                    type: virtio
            - name: console
              attrs:
                type: pty
            - name: channel
              attrs:
                type: unix
              content:
                - name: source
                  attrs:
                    mode: bind
                - name: target
                  attrs:
                    type: virtio
                    name: org.qemu.guest_agent.0
            - name: rng
              attrs:
                model: virtio
              content:
                - name: backend
                  attrs:
                    model: random
                  content: /dev/urandom
```

## License

This work is licensed under the [MIT license](LICENSE).

## Author Information

- [Tim Neumann (neumantm)](https://github.com/neumantm) _tim.neumann@stuvus.uni-stuttgart.de_
