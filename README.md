# Utilities [![Translation status](https://hosted.weblate.org/widgets/hellosystem/-/utilities/svg-badge.svg)](https://hosted.weblate.org/engage/hellosystem/)

Utilities written in PyQt5, meant for use with [hello](https://github.com/probonopd/hello/).

This is a work in progress.

* No compilation needed, since PyQt5
* Focus on simplicity for the user
* Focus on simplicity in source code
* One Python source code file per app
* Tested on FreeBSD in [hello](https://github.com/probonopd/hello/)

Pull requests welcome.

## Boot Environments.app

Simple settings for ZFS Boot Environments.

![image](https://user-images.githubusercontent.com/2480569/97612525-d2e93180-1a17-11eb-90c4-5dd90ad67d7f.png)

## Create Live Medium.app

Simple tool to download a Live ISO and write it to a device (e.g., USB stick) in one go.

## Install FreeBSD.app

Simple installer to install the Live ISO to disk.

## Keyboard.app

Simple Keyboard Layout chooser

![](https://miro.medium.com/max/318/1*AoZTtzHCKAItIeJbOjxpsA.png)

## Sharing.app

Simple tool to set the hostname, enable/disable sshd, enable/disable x11vnc server

## Zeroconf.app

Simple Zeroconf browser

![image](https://user-images.githubusercontent.com/2480569/94365262-a025e380-00cf-11eb-81e0-495f2ee8242b.png)

## Managing redundancy

Some files are intentionally redundant in each application bundle, so that each application bundle is standalone. The redundant files can be converted to hardlinks using

```
hardlink . -v -t -n # Dry run (change nothing, only explain)
hardlink . -v -t
```

This can be useful for making a change in all of the redundant copies at once.
