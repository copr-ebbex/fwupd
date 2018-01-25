%global glib2_version 2.45.8
%global libappstream_version 0.7.4
%global libgusb_version 0.2.11
%global libsoup_version 2.51.92
%global colord_version 1.2.12
%global systemd_version 231

%global enable_tests 1
%global enable_dummy 1

# fwupdate is only available on these arches
%ifarch x86_64 aarch64
%global have_uefi 1
%endif

# libsmbios is only available on x86, and fwupdate is available on just x86_64
%ifarch x86_64
%global have_dell 1
%endif

Summary:   Firmware update daemon
Name:      fwupd
Version:   1.0.4
Release:   1%{?dist}
License:   GPLv2+
URL:       https://github.com/hughsie/fwupd
Source0:   http://people.freedesktop.org/~hughsient/releases/%{name}-%{version}.tar.xz

# lets test this with rawhide and see how the server copes
Patch0:    0001-Do-not-use-the-CDN-when-getting-metadata.patch

BuildRequires: docbook-utils
BuildRequires: gettext
BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: libappstream-glib-devel >= %{libappstream_version}
BuildRequires: libgudev1-devel
BuildRequires: libgusb-devel >= %{libgusb_version}
BuildRequires: libsoup-devel >= %{libsoup_version}
BuildRequires: colord-devel >= %{colord_version}
BuildRequires: polkit-devel >= 0.103
BuildRequires: sqlite-devel
BuildRequires: gpgme-devel
BuildRequires: systemd >= %{systemd_version}
BuildRequires: libarchive-devel
BuildRequires: gobject-introspection-devel
BuildRequires: gcab
BuildRequires: valgrind
BuildRequires: valgrind-devel
BuildRequires: elfutils-libelf-devel
BuildRequires: gtk-doc
BuildRequires: libuuid-devel
BuildRequires: gnutls-devel
BuildRequires: gnutls-utils
BuildRequires: meson
BuildRequires: help2man
BuildRequires: json-glib-devel >= %{json_glib_version}

%if 0%{?have_uefi}
BuildRequires: python3 python3-cairo python3-gobject python3-pillow
BuildRequires: pango-devel
BuildRequires: cairo-devel cairo-gobject-devel
BuildRequires: freetype
BuildRequires: fontconfig
BuildRequires: dejavu-sans-fonts
BuildRequires: adobe-source-han-sans-cn-fonts
%endif

%if 0%{?have_dell}
BuildRequires: efivar-devel
BuildRequires: libsmbios-devel >= 2.3.0
%endif

%if 0%{?have_uefi}
BuildRequires: fwupdate-devel >= 7
%endif

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

Requires: glib2%{?_isa} >= %{glib2_version}
Requires: libappstream-glib%{?_isa} >= %{libappstream_version}
Requires: libgusb%{?_isa} >= %{libgusb_version}
Requires: libsoup%{?_isa} >= %{libsoup_version}
Requires: fwupd-labels = %{version}-%{release}
Requires: bubblewrap

Recommends: python3

Obsoletes: fwupd-sign < 0.1.6
Obsoletes: libebitdo < 0.7.5-3
Obsoletes: libdfu < 1.0.0

%description
fwupd is a daemon to allow session software to update device firmware.

%package devel
Summary: Development package for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Obsoletes: libebitdo-devel < 0.7.5-3
Obsoletes: libdfu-devel < 1.0.0

%description devel
Files for development with %{name}.

%package labels
Summary: Rendered labels for display during system firmware updates.
# BuildArch: noarch is disabled as we can get "different" .BMP files even when
# running the build on the same architecture due to the randomness introduced
# by the TTF files.

%description labels
Rendered labels for display during system firmware updates.

%package tests
Summary: Data files for installed tests
BuildArch: noarch

%description tests
Data files for installed tests.

%prep
%setup -q
%patch0 -p1 -b .no-cdn

%build

%meson \
    -Dgtkdoc=true \
    -Dman=true \
%if 0%{?enable_tests}
    -Dtests=true \
%else
    -Dtests=false \
%endif
%if 0%{?enable_dummy}
    -Dplugin_dummy=true \
%else
    -Dplugin_dummy=false \
%endif
    -Dplugin_thunderbolt=true \
%if 0%{?have_uefi}
    -Dplugin_uefi=true \
    -Dplugin_uefi_labels=true \
%else
    -Dplugin_uefi=false \
    -Dplugin_uefi_labels=false \
%endif
%if 0%{?have_dell}
    -Dplugin_dell=true \
    -Dplugin_synaptics=true \
%else
    -Dplugin_dell=false \
    -Dplugin_synaptics=false \
%endif
    -Dplugin_colorhug=true

%meson_build

%if 0%{?enable_tests}
%check
%meson_test
%endif

%install
%meson_install

mkdir -p --mode=0700 $RPM_BUILD_ROOT%{_localstatedir}/lib/fwupd/gnupg

%find_lang %{name}

%post
/sbin/ldconfig
%systemd_post fwupd.service

%preun
%systemd_preun fwupd.service

%postun
/sbin/ldconfig
%systemd_postun_with_restart fwupd.service

%files -f %{name}.lang
%doc README.md AUTHORS NEWS
%license COPYING
%config(noreplace)%{_sysconfdir}/fwupd/daemon.conf
%dir %{_libexecdir}/fwupd
%{_libexecdir}/fwupd/fwupd
%{_bindir}/dfu-tool
%{_bindir}/fwupdmgr
%dir %{_sysconfdir}/fwupd
%dir %{_sysconfdir}/fwupd/remotes.d
%config(noreplace)%{_sysconfdir}/fwupd/remotes.d/fwupd.conf
%config(noreplace)%{_sysconfdir}/fwupd/remotes.d/lvfs.conf
%config(noreplace)%{_sysconfdir}/fwupd/remotes.d/lvfs-testing.conf
%config(noreplace)%{_sysconfdir}/fwupd/remotes.d/vendor.conf
%config(noreplace)%{_sysconfdir}/pki/fwupd
%{_sysconfdir}/pki/fwupd-metadata
%{_sysconfdir}/dbus-1/system.d/org.freedesktop.fwupd.conf
%{_datadir}/fwupd/remotes.d/fwupd/metadata.xml
%{_datadir}/fwupd/remotes.d/vendor/firmware/README.md
%{_datadir}/dbus-1/interfaces/org.freedesktop.fwupd.xml
%{_datadir}/polkit-1/actions/org.freedesktop.fwupd.policy
%{_datadir}/polkit-1/rules.d/org.freedesktop.fwupd.rules
%{_datadir}/dbus-1/system-services/org.freedesktop.fwupd.service
%{_datadir}/man/man1/dfu-tool.1.gz
%{_datadir}/man/man1/fwupdmgr.1.gz
%{_datadir}/metainfo/org.freedesktop.fwupd.metainfo.xml
%{_datadir}/fwupd/firmware-packager
%{_unitdir}/fwupd-offline-update.service
%{_unitdir}/fwupd.service
%{_unitdir}/system-update.target.wants/
%dir %{_localstatedir}/lib/fwupd
%dir %{_datadir}/fwupd/quirks.d
%{_datadir}/fwupd/quirks.d/*.quirk
%{_localstatedir}/lib/fwupd/builder/README.md
%{_libdir}/libfwupd*.so.*
%{_libdir}/girepository-1.0/Fwupd-2.0.typelib
/usr/lib/udev/rules.d/*.rules
%dir %{_libdir}/fwupd-plugins-3
%{_libdir}/fwupd-plugins-3/libfu_plugin_altos.so
%{_libdir}/fwupd-plugins-3/libfu_plugin_amt.so
%{_libdir}/fwupd-plugins-3/libfu_plugin_colorhug.so
%{_libdir}/fwupd-plugins-3/libfu_plugin_csr.so
%if 0%{?have_dell}
%{_libdir}/fwupd-plugins-3/libfu_plugin_dell.so
%endif
%{_libdir}/fwupd-plugins-3/libfu_plugin_dfu.so
%{_libdir}/fwupd-plugins-3/libfu_plugin_ebitdo.so
%{_libdir}/fwupd-plugins-3/libfu_plugin_nitrokey.so
%{_libdir}/fwupd-plugins-3/libfu_plugin_raspberrypi.so
%{_libdir}/fwupd-plugins-3/libfu_plugin_steelseries.so
%if 0%{?have_dell}
%{_libdir}/fwupd-plugins-3/libfu_plugin_synapticsmst.so
%endif
%if 0%{?enable_dummy}
%{_libdir}/fwupd-plugins-3/libfu_plugin_test.so
%endif
%{_libdir}/fwupd-plugins-3/libfu_plugin_thunderbolt.so
%{_libdir}/fwupd-plugins-3/libfu_plugin_thunderbolt_power.so
%{_libdir}/fwupd-plugins-3/libfu_plugin_udev.so
%if 0%{?have_uefi}
%{_libdir}/fwupd-plugins-3/libfu_plugin_uefi.so
%endif
%{_libdir}/fwupd-plugins-3/libfu_plugin_unifying.so
%{_libdir}/fwupd-plugins-3/libfu_plugin_upower.so
%ghost %{_localstatedir}/lib/fwupd/gnupg

%files devel
%{_datadir}/gir-1.0/Fwupd-2.0.gir
%{_datadir}/gtk-doc/html/libfwupd
%{_includedir}/fwupd-1
%{_libdir}/libfwupd*.so
%{_libdir}/pkgconfig/fwupd.pc

%files labels
%if 0%{?have_uefi}
%{_datadir}/locale/*/LC_IMAGES/fwupd*
%endif

%files tests
%dir %{_datadir}/installed-tests/fwupd
%{_datadir}/installed-tests/fwupd/firmware-example.xml.gz
%{_datadir}/installed-tests/fwupd/firmware-example.xml.gz.asc
%{_datadir}/installed-tests/fwupd/*.test
%{_datadir}/installed-tests/fwupd/*.cab
%{_datadir}/installed-tests/fwupd/*.sh
%{_datadir}/installed-tests/fwupd/*.py*

%changelog
* Thu Jan 25 2018 Richard Hughes <richard@hughsie.com> 1.0.4-1
- New upstream release
- Add a device name for locked UEFI devices
- Add D-Bus methods to get and modify the history information
- Allow the user to share firmware update success or failure
- Ask the user to refresh metadata when it is very old
- Never add two devices to the daemon with the same ID
- Rescan supported flags when refreshing metadata
- Store firmware update success and failure to a local database

* Fri Jan 12 2018 Richard Hughes <richard@hughsie.com> 1.0.3-2
- Backport a patch that fixes applying firmware updates using gnome-software.

* Tue Jan 09 2018 Richard Hughes <richard@hughsie.com> 1.0.3-1
- New upstream release
- Add a new plugin to add support for CSR "Driverless DFU"
- Add initial SF30/SN30 Pro support
- Block owned Dell TPM updates
- Choose the correct component from provides matches using requirements
- Do not try to parse huge compressed archive files
- Handle Thunderbolt "native" mode
- Use the new functionality in libgcab >= 1.0 to avoid writing temp files

* Tue Nov 28 2017 Richard Hughes <richard@hughsie.com> 1.0.2-1
- New upstream release
- Add a plugin for the Nitrokey Storage device
- Add quirk for AT32UC3B1256 as used in the RubberDucky
- Add support for the original AVR DFU protocol
- Allow different plugins to claim the same device
- Disable the dell plugin if libsmbios fails
- Fix critical warning when more than one remote fails to load
- Ignore useless Thunderbolt device types
- Set environment variables to allow easy per-plugin debugging
- Show a nicer error message if the requirement fails
- Sort the output of GetUpgrades correctly
- Use a SHA1 hash for the internal DeviceID

* Thu Nov 09 2017 Kalev Lember <klember@redhat.com> 1.0.1-3
- Rebuild against libappstream-glib 0.7.4

* Thu Nov 09 2017 Kalev Lember <klember@redhat.com> 1.0.1-2
- Fix libdfu obsoletes versions

* Thu Nov 09 2017 Richard Hughes <richard@hughsie.com> 1.0.1-1
- New upstream release
- Add support for HWID requirements
- Add support for programming various AVR32 and XMEGA parts using DFU
- Add the various DFU quirks for the Jabra Speak devices
- Catch invalid Dell dock component requests
- Correctly output Intel HEX files with > 16bit offset addresses
- Do not try to verify the element write if upload is unsupported
- Fix a double-unref when updating any 8Bitdo device
- Fix uploading large firmware files over DFU
- Format the BCD USB revision numbers correctly
- Guess the DFU transfer size if it is not specified
- Include the reset timeout as wValue to fix some DFU bootloaders
- Move the database of supported devices out into runtime loaded files
- Support devices with truncated DFU interface data
- Use the correct wDetachTimeOut when writing DFU firmware
- Verify devices with legacy VIDs are actually 8Bitdo controllers

* Mon Oct 09 2017 Richard Hughes <richard@hughsie.com> 1.0.0-1
- New upstream release
- This release breaks API and ABI to remove deprecated symbols
- libdfu is now not installed as a shared library
- Add FuDeviceLocker to simplify device open/close lifecycles
- Add functionality to blacklist Dell HW with problems
- Disable the fallback USB plugin
- Do not fail to load the daemon if cached metadata is invalid
- Do not use system-specific infomation for UEFI PCI devices
- Fix various printing issues with the progressbar
- Never fallback to an offline update from client code
- Only set the Dell coldplug delay when we know we need it
- Parse the SMBIOS v2 and v3 DMI tables directly
- Support uploading the UEFI firmware splash image
- Use the intel-wmi-thunderbolt kernel module to force power

* Fri Sep 01 2017 Richard Hughes <richard@hughsie.com> 0.9.7-1
- New upstream release
- Add a FirmwareBaseURI parameter to the remote config
- Add a firmware builder that uses bubblewrap
- Add a python script to create fwupd compatible cab files from .exe files
- Add a thunderbolt plugin for new kernel interface
- Fix an incomplete cipher when using XTEA on data not in 4 byte chunks
- Show a bouncing progress bar if the percentage remains at zero
- Use the new bootloader PIDs for Unifying pico receivers

* Fri Sep 01 2017 Kalev Lember <klember@redhat.com> 0.9.6-2
- Disable i686 UEFI support now that fwupdate is no longer available there
- Enable aarch64 UEFI support now that all the deps are available there

* Thu Aug 03 2017 Richard Hughes <richard@hughsie.com> 0.9.6-1
- New upstream release
- Add --version option to fwupdmgr
- Display all errors recorded by efi_error tracing
- Don't log a warning when an unknown unifying report is parsed
- Fix a hang on 32 bit machines
- Make sure the unifying percentage completion goes from 0% to 100%
- Support embedded devices with local firmware metadata
- Use new GUsb functionality to fix flashing Unifying devices

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Jul 04 2017 Richard Hughes <richard@hughsie.com> 0.9.5-1
- New upstream release
- Add a plugin to get the version of the AMT ME interface
- Allow flashing Unifying devices in bootloader modes
- Filter by Unifying SwId when making HID++2.0 requests
- Fix downgrades when version_lowest is set
- Fix the self tests when running on PPC64 big endian
- Use the UFY DeviceID prefix for Unifying devices

* Thu Jun 15 2017 Richard Hughes <richard@hughsie.com> 0.9.4-1
- New upstream release
- Add installed tests that use the daemon
- Add the ability to restrict firmware to specific vendors
- Compile with newer versions of meson
- Fix a common crash when refreshing metadata
- Generate a images for status messages during system firmware update
- Show progress download when refreshing metadata
- Use the correct type signature in the D-Bus introspection file

* Wed Jun 07 2017 Richard Hughes <richard@hughsie.com> 0.9.3-1
- New upstream release
- Add a 'downgrade' command to fwupdmgr
- Add a 'get-releases' command to fwupdmgr
- Add support for Microsoft HardwareIDs
- Allow downloading metadata from more than just the LVFS
- Allow multiple checksums on devices and releases
- Correctly open Unifying devices with original factory firmware
- Do not expect a Unifying reply when issuing a REBOOT command
- Do not re-download firmware that exists in the cache
- Fix a problem when testing for a Dell system
- Fix flashing new firmware to 8bitdo controllers

* Tue May 23 2017 Richard Hughes <richard@hughsie.com> 0.9.2-2
- Backport several fixes for updating Unifying devices

* Mon May 22 2017 Richard Hughes <richard@hughsie.com> 0.9.2-1
- New upstream release
- Add support for Unifying DFU features
- Do not spew a critial warning when parsing an invalid URI
- Ensure steelseries device is closed if it returns an invalid packet
- Ignore spaces in the Unifying version prefix

* Thu Apr 20 2017 Richard Hughes <richard@hughsie.com> 0.8.2-1
- New upstream release
- Add a config option to allow runtime disabling plugins by name
- Add DFU quirk for OpenPICC and SIMtrace
- Create directories in /var/cache as required
- Fix the Requires lines in the dfu pkg-config file
- Only try to mkdir the localstatedir if we have the right permissions
- Support proxy servers in fwupdmgr

* Thu Mar 23 2017 Bastien Nocera <bnocera@redhat.com> - 0.8.1-2
+ fwupd-0.8.1-2
- Release claimed devices on error, fixes unusable input devices

* Mon Feb 27 2017 Richard Hughes <richard@hughsie.com> 0.8.1-1
- New upstream release
- Adjust systemd confinement restrictions
- Don't initialize libsmbios on unsupported systems
- Fix a crash when enumerating devices

* Wed Feb 08 2017 Richard Hughes <richard@hughsie.com> 0.8.0-1
- New upstream release
- Add support for Intel Thunderbolt devices
- Add support for Logitech Unifying devices
- Add support for Synaptics MST cascades hubs
- Add support for the Altus-Metrum ChaosKey device
- Always close USB devices before error returns
- Return the pending UEFI update when not on AC power
- Use a heuristic for the start address if the firmware has no DfuSe footer
- Use more restrictive settings when running under systemd

* Sat Dec 10 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.7.5-2
- Rebuild for gpgme 1.18

* Wed Oct 19 2016 Richard Hughes <richard@hughsie.com> 0.7.5-1
- New upstream release
- Add quirks for HydraBus as it does not have a DFU runtime
- Don't create the UEFI dummy device if the unlock will happen on next boot
- Fix an assert when unlocking the dummy ESRT device
- Fix writing firmware to devices using the ST reference bootloader
- Match the Dell TB16 device

* Mon Sep 19 2016 Richard Hughes <richard@hughsie.com> 0.7.4-1
- New upstream release
- Add a fallback for older appstream-glib releases
- Allow the argument to 'dfu-tool set-release' be major.minor
- Fix a possible crash when uploading firmware files using libdfu
- Fix libfwupd self tests when a host-provided fwupd is not available
- Load the Altos USB descriptor from ELF files
- Show the human-readable version in the 'dfu-tool dump' output
- Support writing the IHEX symbol table
- Write the ELF files with the correct section type

* Mon Aug 29 2016 Kalev Lember <klember@redhat.com> 0.7.3-2
- Fix an unexpanded macro in the spec file
- Tighten libebitdo-devel requires with the _isa macro
- Add ldconfig scripts for libdfu and libebitdo subpackages

* Mon Aug 29 2016 Richard Hughes <richard@hughsie.com> 0.7.3-1
- New upstream release
- Add Dell TPM and TB15/WD15 support via new Dell provider
- Add initial ELF reading and writing support to libdfu
- Add support for installing multiple devices from a CAB file
- Allow providers to export percentage completion
- Don't fail while checking versions or locked state
- Show a progress notification when installing firmware
- Show the vendor flashing instructions when installing
- Use a private gnupg key store
- Use the correct firmware when installing a composite device

* Fri Aug 19 2016 Peter Jones <pjones@redhat.com> - 0.7.2-6
- Rebuild to get libfwup.so.1 as our fwupdate dep.  This should make this the
  last time we need to rebuild for this.

* Wed Aug 17 2016 Peter Jones <pjones@redhat.com> - 0.7.2-5
- rebuild against new efivar and fwupdate

* Fri Aug 12 2016 Adam Williamson <awilliam@redhat.com> - 0.7.2-4
- rebuild against new efivar and fwupdate

* Thu Aug 11 2016 Richard Hughes <richard@hughsie.com> 0.7.2-3
- Use the new CDN for firmware metadata

* Thu Jul 14 2016 Kalev Lember <klember@redhat.com> - 0.7.2-2
- Tighten subpackage dependencies

* Mon Jun 13 2016 Richard Hughes <richard@hughsie.com> 0.7.2-1
- New upstream release
- Allow devices to have multiple assigned GUIDs
- Allow metainfo files to match only specific revisions of devices
- Only claim the DFU interface when required
- Only return updatable devices from GetDevices()
- Show the DFU protocol version in 'dfu-tool list'

* Fri May 13 2016 Richard Hughes <richard@hughsie.com> 0.7.1-1
- New upstream release
- Add device-added, device-removed and device-changed signals
- Add for a new device field "Flashes Left"
- Fix a critical warning when restarting the daemon
- Fix BE issues when reading and writing DFU files
- Make the device display name nicer
- Match the AppStream metadata after a device has been added
- Return all update descriptions newer than the installed version
- Set the device description when parsing local firmware files

* Fri Apr 01 2016 Richard Hughes <richard@hughsie.com> 0.7.0-1
- New upstream release
- Add Alienware to the version quirk table
- Add a version plugin for SteelSeries hardware
- Do not return updates that require AC when on battery
- Return the device flags when getting firmware details

* Mon Mar 14 2016 Richard Hughes <richard@hughsie.com> 0.6.3-1
- New upstream release
- Add an unlock method for devices
- Add ESRT enable method into UEFI provider
- Correct the BCD version number for DFU 1.1
- Ignore the DFU runtime on the DW1820A
- Only read PCI OptionROM firmware when devices are manually unlocked
- Require AC power before scheduling some types of firmware update

* Fri Feb 12 2016 Richard Hughes <richard@hughsie.com> 0.6.2-1
- New upstream release
- Add 'Created' and 'Modified' properties on managed devices
- Fix get-results for UEFI provider
- Support vendor-specific UEFI version encodings

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.6.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Jan 19 2016 Richard Hughes <richard@hughsie.com> 0.6.1-1
- New upstream release
- Do not misdetect different ColorHug devices
- Only dump the profiling data when run with --verbose

* Mon Dec 07 2015 Richard Hughes <richard@hughsie.com> 0.6.0-1
- New upstream release
- Add support for automatically updating USB DFU-capable devices
- Emit the changed signal after doing an update
- Export the AppStream ID when returning device results
- Use the same device identification string format as Microsoft

* Wed Nov 18 2015 Richard Hughes <richard@hughsie.com> 0.5.4-1
- New upstream release
- Use API available in fwupdate 0.5 to avoid writing temp files
- Fix compile error against fwupdate 0.5 due to API bump

* Thu Nov 05 2015 Richard Hughes <richard@hughsie.com> 0.5.3-1
- New upstream release
- Avoid seeking when reading the file magic during refresh
- Do not assume that the compressed XML data will be NUL terminated
- Use the correct user agent string for fwupdmgr

* Wed Oct 28 2015 Richard Hughes <richard@hughsie.com> 0.5.2-1
- New upstream release
- Add the update description to the GetDetails results
- Clear the in-memory firmware store only after parsing a valid XML file
- Ensure D-Bus remote errors are registered at fwupdmgr startup
- Fix verify-update to produce components with the correct provide values
- Show the dotted-decimal representation of the UEFI version number
- Support cabinet archives files with more than one firmware

* Mon Sep 21 2015 Richard Hughes <richard@hughsie.com> 0.5.1-1
- Update to 0.5.1 to fix a bug in the offline updater

* Tue Sep 15 2015 Richard Hughes <richard@hughsie.com> 0.5.0-1
- New upstream release
- Do not reboot if racing with the PackageKit offline update mechanism

* Thu Sep 10 2015 Richard Hughes <richard@hughsie.com> 0.1.6-3
- Do not merge the existing firmware metadata with the submitted files

* Thu Sep 10 2015 Kalev Lember <klember@redhat.com> 0.1.6-2
- Own system-update.target.wants directory
- Make fwupd-sign obsoletes versioned

* Thu Sep 10 2015 Richard Hughes <richard@hughsie.com> 0.1.6-1
- New upstream release
- Add application metadata when getting the updates list
- Remove fwsignd, we have the LVFS now

* Fri Aug 21 2015 Kalev Lember <klember@redhat.com> 0.1.5-3
- Disable fwupd offline update service

* Wed Aug 19 2015 Richard Hughes <richard@hughsie.com> 0.1.5-2
- Use the non-beta download URL prefix

* Wed Aug 12 2015 Richard Hughes <richard@hughsie.com> 0.1.5-1
- New upstream release
- Add a Raspberry Pi firmware provider
- Fix validation of written firmware
- Make parsing the option ROM runtime optional
- Use the AppStream 0.9 firmware specification by default

* Sat Jul 25 2015 Richard Hughes <richard@hughsie.com> 0.1.4-1
- New upstream release
- Actually parse the complete PCI option ROM
- Add a 'fwupdmgr update' command to update all devices to latest versions
- Add a simple signing server that operates on .cab files
- Add a 'verify' command that verifies the cryptographic hash of device firmware

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.1.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Jun 03 2015 Richard Hughes <richard@hughsie.com> 0.1.3-2
- Compile with libfwupdate for UEFI firmware support.

* Thu May 28 2015 Richard Hughes <richard@hughsie.com> 0.1.3-1
- New upstream release
- Coldplug the devices before acquiring the well known name
- Run the offline actions using systemd when required
- Support OpenHardware devices using the fwupd vendor extensions

* Wed Apr 22 2015 Richard Hughes <richard@hughsie.com> 0.1.2-1
- New upstream release
- Only allow signed firmware to be upgraded without a password

* Mon Mar 23 2015 Richard Hughes <richard@hughsie.com> 0.1.1-1
- New upstream release
- Add a 'get-updates' command to fwupdmgr
- Add and document the offline-update lifecycle
- Create a libfwupd shared library
- Create runtime directories if they do not exist
- Do not crash when there are no devices to return

* Mon Mar 16 2015 Richard Hughes <richard@hughsie.com> 0.1.0-1
- First release
