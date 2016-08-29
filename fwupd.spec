%global glib2_version 2.45.8
%global libappstream_version 0.5.10
%global libgusb_version 0.2.9
%global libsoup_version 2.51.92

Summary:   Firmware update daemon
Name:      fwupd
Version:   0.7.3
Release:   2%{?dist}
License:   GPLv2+
URL:       https://github.com/hughsie/fwupd
Source0:   http://people.freedesktop.org/~hughsient/releases/%{name}-%{version}.tar.xz

BuildRequires: docbook-utils
BuildRequires: gettext
BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: intltool
BuildRequires: libappstream-glib-devel >= %{libappstream_version}
BuildRequires: libgudev1-devel
BuildRequires: libgusb-devel >= %{libgusb_version}
BuildRequires: libsoup-devel >= %{libsoup_version}
BuildRequires: colord-devel >= 1.0.0
BuildRequires: polkit-devel >= 0.103
BuildRequires: libgcab1-devel
BuildRequires: sqlite-devel
BuildRequires: gpgme-devel
BuildRequires: systemd
BuildRequires: libarchive-devel
BuildRequires: gobject-introspection-devel
BuildRequires: gcab
BuildRequires: valgrind
BuildRequires: elfutils-libelf-devel
BuildRequires: gtk-doc

%ifarch x86_64 %{ix86}
BuildRequires: libsmbios-devel >= 2.3.0
%endif

%ifarch x86_64 %{ix86} aarch64
BuildRequires: fwupdate-devel >= 7
%endif

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

Requires: libdfu%{?_isa} = %{version}-%{release}
Requires: glib2%{?_isa} >= %{glib2_version}
Requires: libappstream-glib%{?_isa} >= %{libappstream_version}
Requires: libgusb%{?_isa} >= %{libgusb_version}
Requires: libsoup%{?_isa} >= %{libsoup_version}

Obsoletes: fwupd-sign < 0.1.6

%description
fwupd is a daemon to allow session software to update device firmware.

%package devel
Summary: Development package for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
Files for development with %{name}.

%package -n libdfu
Summary: A library for DFU

%description -n libdfu
A library for updating USB devices using DFU.

%package -n libdfu-devel
Summary: Development package for libdfu
Requires: libdfu%{?_isa} = %{version}-%{release}

%description -n libdfu-devel
Files for development with libdfu.

%package -n libebitdo
Summary: A library for accessing 8Bitdo hardware

%description -n libebitdo
A library for updating 8Bitdo USB devices.

%package -n libebitdo-devel
Summary: Development package for libebitdo
Requires: libebitdo = %{version}-%{release}

%description -n libebitdo-devel
Files for development with libebitdo.

%prep
%setup -q

%build
%configure \
        --disable-static        \
        --enable-gtk-doc        \
        --enable-colorhug       \
%ifarch x86_64 %{ix86} aarch64
        --enable-uefi           \
%else
        --disable-uefi          \
%endif
%ifarch x86_64 %{ix86}
        --enable-dell           \
%else
        --disable-dell          \
%endif
        --disable-rpath         \
        --disable-silent-rules  \
        --disable-dependency-tracking

make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT
find %{buildroot} -name '*.la' -exec rm -f {} ';'
mkdir --mode=0700 $RPM_BUILD_ROOT%{_localstatedir}/lib/fwupd/gnupg

%find_lang %{name}

%check
make check VERBOSE=1

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
%config(noreplace)%{_sysconfdir}/fwupd.conf
%dir %{_libexecdir}/fwupd
%{_libexecdir}/fwupd/fwupd
%{_bindir}/fwupdmgr
%{_sysconfdir}/pki/fwupd
%{_sysconfdir}/pki/fwupd-metadata
%{_sysconfdir}/dbus-1/system.d/org.freedesktop.fwupd.conf
%{_datadir}/app-info/xmls/org.freedesktop.fwupd.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.fwupd.xml
%{_datadir}/polkit-1/actions/org.freedesktop.fwupd.policy
%{_datadir}/polkit-1/rules.d/org.freedesktop.fwupd.rules
%{_datadir}/dbus-1/system-services/org.freedesktop.fwupd.service
%{_datadir}/man/man1/fwupdmgr.1.gz
%{_unitdir}/fwupd-offline-update.service
%{_unitdir}/fwupd.service
%{_unitdir}/system-update.target.wants/
%dir %{_localstatedir}/lib/fwupd
%{_libdir}/libfwupd*.so.*
%{_libdir}/girepository-1.0/Fwupd-1.0.typelib
%dir %{_localstatedir}/cache/app-info
%dir %{_localstatedir}/cache/app-info/icons
%dir %{_localstatedir}/cache/app-info/xmls
/usr/lib/udev/rules.d/*.rules
%dir %{_libdir}/fwupd-plugins-1
%{_libdir}/fwupd-plugins-1/*.so
%ghost %{_localstatedir}/lib/fwupd/gnupg

%files devel
%{_datadir}/gir-1.0/Fwupd-1.0.gir
%{_datadir}/gtk-doc/html/libfwupd
%{_includedir}/fwupd-1
%{_libdir}/libfwupd*.so
%{_libdir}/pkgconfig/fwupd.pc

%files -n libdfu
%{_bindir}/dfu-tool
%{_datadir}/man/man1/dfu-tool.1.gz
%{_libdir}/girepository-1.0/Dfu-1.0.typelib
%{_libdir}/libdfu*.so.*

%files -n libdfu-devel
%{_datadir}/gir-1.0/Dfu-1.0.gir
%{_datadir}/gtk-doc/html/libdfu
%dir %{_includedir}/libdfu
%{_includedir}/dfu.h
%{_includedir}/libdfu/*.h
%{_libdir}/libdfu*.so
%{_libdir}/pkgconfig/dfu.pc

%files -n libebitdo
%{_bindir}/ebitdo-tool
%{_libdir}/libebitdo*.so.*

%files -n libebitdo-devel
%dir %{_includedir}/libebitdo
%{_includedir}/ebitdo.h
%{_includedir}/libebitdo/*.h
%{_libdir}/libebitdo*.so
%{_libdir}/pkgconfig/ebitdo.pc

%changelog
* Mon Aug 29 2016 Kalev Lember <klember@redhat.com> 0.7.3-2
- Fix an unexpanded macro in the spec file

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
