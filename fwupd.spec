Summary:   Firmware update daemon
Name:      fwupd
Version:   0.1.3
Release:   3%{?dist}
License:   GPLv2+
URL:       https://github.com/hughsie/fwupd
Source0:   http://people.freedesktop.org/~hughsient/releases/%{name}-%{version}.tar.xz

BuildRequires: docbook-utils
BuildRequires: gettext
BuildRequires: glib2-devel
BuildRequires: intltool
BuildRequires: libgudev1-devel
BuildRequires: colord-devel >= 1.0.0
BuildRequires: polkit-devel >= 0.103
BuildRequires: libgcab1-devel
BuildRequires: sqlite-devel
BuildRequires: gpgme-devel
BuildRequires: systemd
BuildRequires: gobject-introspection-devel
BuildRequires: libappstream-glib-devel >= 0.3.6

%ifarch x86_64 %{ix86} aarch64
BuildRequires: fwupdate-devel >= 0.4
%endif

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%ifarch x86_64 %{ix86} aarch64
Requires: efibootmgr
%endif

%description
fwupd is a daemon to allow session software to update device firmware.

%package devel
Summary: Development package for %{name}
Requires: %{name} = %{version}-%{release}

%description devel
Files for development with %{name}.

%prep
%setup -q

%build
%configure \
        --disable-static        \
%ifnarch x86_64 %{ix86} aarch64
        --disable-uefi          \
%endif
        --disable-rpath         \
        --disable-silent-rules  \
        --disable-dependency-tracking

make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT
find %{buildroot} -name '*.la' -exec rm -f {} ';'

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
%{_libexecdir}/fwupd
%{_bindir}/fwupdmgr
%{_sysconfdir}/pki/fwupd
%{_sysconfdir}/dbus-1/system.d/org.freedesktop.fwupd.conf
%{_datadir}/dbus-1/interfaces/org.freedesktop.fwupd.xml
%{_datadir}/polkit-1/actions/org.freedesktop.fwupd.policy
%{_datadir}/polkit-1/rules.d/org.freedesktop.fwupd.rules
%{_datadir}/dbus-1/system-services/org.freedesktop.fwupd.service
%{_datadir}/man/man1/fwupdmgr.1.gz
%{_unitdir}/*.service
%{_unitdir}/system-update.target.wants/*.service
%dir %{_localstatedir}/lib/fwupd
%{_libdir}/lib*.so.*
%{_libdir}/girepository-1.0/*.typelib

%files devel
%{_includedir}/fwupd-1
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*.pc
%{_datadir}/gir-1.0/*.gir

%changelog
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
