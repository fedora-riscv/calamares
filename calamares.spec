%global snapdate 20141115
%global snaphash 6b2ccfb442defc1ffeb9359edd892aae5335b838
%global partitionmanagerhash 3f1ace00592088a920f731acb1e42417f71f5e62

Name:           calamares
Version:        0
Release:        0.13.%{snapdate}git%(echo %{snaphash} | cut -c -13)%{?dist}
Summary:        Installer from a live CD/DVD/USB to disk

License:        GPLv3+
URL:            http://calamares.github.io/
Source0:        https://github.com/calamares/calamares/archive/%{snaphash}/calamares-%{snaphash}.tar.gz
Source1:        https://github.com/calamares/partitionmanager/archive/%{partitionmanagerhash}/calamares-partitionmanager-%{partitionmanagerhash}.tar.gz
# documentation file describing how to rebrand Calamares
Source2:        README.branding

# adjust some default settings (default shipped .conf files)
Patch0:         calamares-default-settings.patch
# .desktop file customizations and fixes (e.g. don't use nonexistent Icon=)
Patch1:         calamares-desktop-file.patch

BuildRequires:  kf5-rpm-macros

BuildRequires:  cmake >= 2.8.12
BuildRequires:  extra-cmake-modules >= 0.0.13

BuildRequires:  qt5-qtbase-devel >= 5.3
BuildRequires:  qt5-qtsvg-devel >= 5.3
BuildRequires:  qt5-qttools-devel >= 5.3
BuildRequires:  polkit-qt5-1-devel

BuildRequires:  kf5-kconfig-devel
BuildRequires:  kf5-kcoreaddons-devel
BuildRequires:  kf5-ki18n-devel
BuildRequires:  kf5-solid-devel

BuildRequires:  pkgconfig
BuildRequires:  gettext

BuildRequires:  python3-devel >= 3.3
BuildRequires:  boost-python3-devel >= 1.55.0
%global __python %{__python3}

BuildRequires:  yaml-cpp-devel >= 0.5.1
BuildRequires:  libblkid-devel
BuildRequires:  libatasmart-devel
BuildRequires:  parted-devel

BuildRequires:  desktop-file-utils

Requires:       coreutils
Requires:       util-linux
Requires:       sddm
Requires:       dracut
Requires:       grub2
Requires:       console-setup
Requires:       xorg-x11-xkb-utils
Requires:       NetworkManager
Requires:       os-prober
Requires:       e2fsprogs
Requires:       dosfstools
Requires:       ntfsprogs
Requires:       gawk
Requires:       systemd
Requires:       rsync
Requires:       shadow-utils
Requires:       polkit

Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

%description
Calamares is a distribution-independent installer framework, designed to install
from a live CD/DVD/USB environment to a hard disk. It includes a graphical
installation program based on Qt 5. This package includes the Calamares
framework and the required configuration files to produce a working replacement
for Anaconda's liveinst.


%package        libs
Summary:        Calamares runtime libraries
Requires:       %{name} = %{version}-%{release}

%description    libs
%{summary}.


%package        devel
Summary:        Development files for %{name}
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       cmake

%description    devel
The %{name}-devel package contains libraries and header files for
developing custom modules for Calamares.


%prep
%setup -q -n %{name}-%{snaphash} -a 1
rmdir src/modules/partition/partitionmanager
mv -f partitionmanager-%{partitionmanagerhash} src/modules/partition/partitionmanager
cp -pf %{SOURCE2} .
%patch0 -p1 -b .default-settings
%patch1 -p1 -b .desktop-file
# delete backup files so they don't get installed
rm -f src/modules/*/*.conf.default-settings

%build
mkdir -p %{_target_platform}
pushd %{_target_platform}
%{cmake_kf5} -DWITH_PARTITIONMANAGER:BOOL="ON" -DCMAKE_BUILD_TYPE:STRING="RelWithDebInfo" ..
popd

make %{?_smp_mflags} -C %{_target_platform}

%install
make install/fast DESTDIR=%{buildroot} -C %{_target_platform}
# own the local settings directories
mkdir -p %{buildroot}%{_sysconfdir}/calamares/modules
mkdir -p %{buildroot}%{_sysconfdir}/calamares/branding

%check
# validate the .desktop file
desktop-file-validate %{buildroot}%{_datadir}/applications/calamares.desktop

%post
# write /etc/default/grub if missing
# works around https://github.com/calamares/calamares/issues/128
if [ ! -e %{_sysconfdir}/default/grub ] ; then
  cat >%{_sysconfdir}/default/grub <<EOF
GRUB_TIMEOUT=5
GRUB_DISTRIBUTOR="\$(sed 's, release .*\$,,g' /etc/system-release)"
GRUB_DEFAULT=saved
GRUB_DISABLE_SUBMENU=true
GRUB_TERMINAL_OUTPUT="console"
GRUB_CMDLINE_LINUX="vconsole.font=latarcyrheb-sun16 \$([ -x /usr/sbin/rhcrashkernel-param ] && /usr/sbin/rhcrashkernel-param || :) rhgb quiet"
GRUB_DISABLE_RECOVERY="true"
EOF
fi

%files
%doc LICENSE AUTHORS README.branding
%{_bindir}/calamares
%{_datadir}/calamares/
%{_datadir}/applications/calamares.desktop
%{_datadir}/polkit-1/actions/com.github.calamares.calamares.policy
%{_sysconfdir}/calamares/

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files libs
%{_libdir}/libcalamares.so.*
%{_libdir}/libcalamaresui.so.*
# unversioned library
%{_libdir}/libcalapm.so
%{_libdir}/calamares/

%files devel
%{_includedir}/libcalamares/
%{_libdir}/libcalamares.so
%{_libdir}/libcalamaresui.so
%{_libdir}/cmake/Calamares/


%changelog
* Sat Nov 15 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0-0.13.20141115git6b2ccfb442def
- New snapshot, adds retranslation support to more modules, fixes writing
  /etc/hosts, writes /etc/locale.conf (always LANG=en_US.UTF-8 for now)
- Drop grub2-tools (calamares#123) patch, names made configurable upstream
- Update default-settings patch to set the grub2 names and handle new modules
- Drop workaround recreating calamares/libcalamares.so symlink, fixed upstream
- Move desktop-file-validate call to %%check

* Tue Nov 11 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0-0.12.20141111gitfaa77d7f5e656
- New snapshot, writes keyboard configuration files to the installed system
  (calamares#31), adds a language selector and dynamic retranslation support

* Fri Nov 07 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0-0.11.20141107gitfd5d1935290d9
- New snapshot, fixes the calamares#132 fix again, fixes enabling translations

* Thu Nov 06 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0-0.10.20141106git1df44eddba572
- New snapshot, fixes the calamares#132 fix, calamares#124 (colors in build.log)
- Drop pkexec policy rename from desktop-file patch, fixed upstream

* Wed Nov 05 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0-0.9.20141104gitb9af5b7d544a7
- New snapshot, creates sddm.conf if missing (calamares#132), adds translations
- Use and customize the new upstream .desktop file
- Point URL to the new http://calamares.github.io/ page

* Tue Oct 28 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0-0.8.20141028git10ca85338db00
- New snapshot, fixes FTBFS in Rawhide (Qt 5.4.0 beta) (calamares#125)

* Tue Oct 28 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0-0.7.20141027git6a9c9cbaae0a9
- Add a README.branding documenting how to rebrand Calamares

* Mon Oct 27 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0-0.6.20141027git6a9c9cbaae0a9
- New snapshot, device-source patch (calamares#127) upstreamed

* Thu Oct 23 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0-0.5.20141020git89fe455163c62
- Disable startup notification, does not work properly with pkexec

* Wed Oct 22 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0-0.4.20141020git89fe455163c62
- Add a .desktop file that live kickstarts can use to show a menu entry or icon

* Mon Oct 20 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0-0.3.20141020git89fe455163c62
- New snapshot, fixes escape sequences in g++ diagnostics in the build.log
- Allow using devices as sources for unpackfs, fixes failure to install
- Write /etc/default/grub in %%post if missing, fixes another install failure
- Fix the path to grub.cfg, fixes another install failure
- Own /etc/calamares/branding/

* Mon Oct 20 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0-0.2.20141017git8a623cc1181e9
- Pass -DWITH_PARTITIONMANAGER:BOOL="ON"
- Pass -DCMAKE_BUILD_TYPE:STRING="RelWithDebInfo"
- Remove unnecessary Requires: kf5-filesystem

* Mon Oct 20 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0-0.1.20141017git8a623cc1181e9
- Initial package
