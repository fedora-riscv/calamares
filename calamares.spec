#global snapdate 20150502
#global snaphash a70306e54f505bb296700bb6986af7055bdbdf85
#global partitionmanagerhash 3f1ace00592088a920f731acb1e42417f71f5e62

Name:           calamares
Version:        1.1.3
Release:        1%{?snaphash:.%{snapdate}git%(echo %{snaphash} | cut -c -13)}%{?dist}
Summary:        Installer from a live CD/DVD/USB to disk

License:        GPLv3+
URL:            http://calamares.io/
Source0:        https://github.com/calamares/calamares/%{?snaphash:archive}%{!?snaphash:releases/download}/%{?snaphash}%{!?snaphash:v%{version}}/calamares-%{?snaphash}%{!?snaphash:%{version}}.tar.gz
%if %{?partitionmanagerhash:1}%{!?partitionmanagerhash:0}
Source1:        https://github.com/calamares/partitionmanager/archive/%{partitionmanagerhash}/calamares-partitionmanager-%{partitionmanagerhash}.tar.gz
%endif
Source2:        show.qml
# Run:
# lupdate-qt5 show.qml -ts calamares-auto_fr.ts
# then translate the template in linguist-qt5.
Source3:        calamares-auto_fr.ts
# Run:
# lupdate-qt5 show.qml -ts calamares-auto_de.ts
# then translate the template in linguist-qt5.
Source4:        calamares-auto_de.ts
# Run:
# lupdate-qt5 show.qml -ts calamares-auto_it.ts
# then translate the template in linguist-qt5.
Source5:        calamares-auto_it.ts

# adjust some default settings (default shipped .conf files)
Patch0:         calamares-1.1.3-default-settings.patch
# .desktop file customizations and fixes (e.g. don't use nonexistent Icon=)
Patch1:         calamares-desktop-file.patch

# Calamares is only supported where live images (and GRUB) are. (#1171380)
# This list matches the livearches global from anaconda.spec
ExclusiveArch:  %{ix86} x86_64 ppc ppc64 ppc64le

BuildRequires:  kf5-rpm-macros

BuildRequires:  cmake >= 2.8.12
BuildRequires:  extra-cmake-modules >= 0.0.13

BuildRequires:  qt5-qtbase-devel >= 5.3
BuildRequires:  qt5-qtdeclarative-devel >= 5.3
BuildRequires:  qt5-qtsvg-devel >= 5.3
BuildRequires:  qt5-qttools-devel >= 5.3
BuildRequires:  qt5-qtwebkit-devel >= 5.3
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

# for automatic branding setup
Requires(post): system-release
Requires(post): system-logos
Requires:       system-logos

Requires:       coreutils
Requires:       util-linux
Requires:       dmidecode
Requires:       upower
Requires:       NetworkManager
Requires:       dracut
Requires:       grub2
%ifarch x86_64
# EFI currently only supported on x86_64
Requires:       grub2-efi
%endif
Requires:       gdisk
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
%if 0%{?fedora} > 21
Requires:       dnf
%else
%global use_yum 1
Requires:       yum
%endif

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


%package        webview
Summary:        Calamares webview module
Requires:       %{name} = %{version}-%{release}
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

%description    webview
Optional webview module for the Calamares installer, based on Qt5WebKit.


%package        devel
Summary:        Development files for %{name}
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       cmake

%description    devel
The %{name}-devel package contains libraries and header files for
developing custom modules for Calamares.


%prep
%setup -q %{?snaphash:-n %{name}-%{snaphash}} %{?partitionmanagerhash:-a 1}
%if %{?partitionmanagerhash:1}%{!?partitionmanagerhash:0}
rmdir src/modules/partition/partitionmanager
mv -f partitionmanager-%{partitionmanagerhash} src/modules/partition/partitionmanager
%endif
%patch0 -p1 -b .default-settings
%patch1 -p1 -b .desktop-file
# delete backup files so they don't get installed
rm -f src/modules/*/*.conf.default-settings
%if 0%{?use_yum}
sed -i -e 's/^backend: dnf$/backend: yum/g' src/modules/packages/packages.conf
%endif

%build
mkdir -p %{_target_platform}
pushd %{_target_platform}
%{cmake_kf5} -DWITH_PARTITIONMANAGER:BOOL="ON" -DCMAKE_BUILD_TYPE:STRING="RelWithDebInfo" ..
popd

make %{?_smp_mflags} -C %{_target_platform}

%install
make install/fast DESTDIR=%{buildroot} -C %{_target_platform}
# create the auto branding directory
mkdir -p %{buildroot}%{_datadir}/calamares/branding/auto
touch %{buildroot}%{_datadir}/calamares/branding/auto/branding.desc
install -p -m 644 %{SOURCE2} %{buildroot}%{_datadir}/calamares/branding/auto/show.qml
mkdir -p %{buildroot}%{_datadir}/calamares/branding/auto/lang
lrelease-qt5 %{SOURCE3} -qm %{buildroot}%{_datadir}/calamares/branding/auto/lang/calamares-auto_fr.qm
lrelease-qt5 %{SOURCE4} -qm %{buildroot}%{_datadir}/calamares/branding/auto/lang/calamares-auto_de.qm
lrelease-qt5 %{SOURCE5} -qm %{buildroot}%{_datadir}/calamares/branding/auto/lang/calamares-auto_it.qm
# own the local settings directories
mkdir -p %{buildroot}%{_sysconfdir}/calamares/modules
mkdir -p %{buildroot}%{_sysconfdir}/calamares/branding

%check
# validate the .desktop file
desktop-file-validate %{buildroot}%{_datadir}/applications/calamares.desktop

%post
# generate the "auto" branding
. %{_sysconfdir}/os-release

LOGO=%{_datadir}/pixmaps/fedora-logo.png

if [ -e %{_datadir}/pixmaps/fedora-logo-sprite.png ] ; then
  SPRITE="%{_datadir}/pixmaps/fedora-logo-sprite.png"
else
  SPRITE="%{_datadir}/calamares/branding/default/squid.png"
fi

if [ -n "$HOME_URL" ] ; then
  PRODUCTURL="$HOME_URL"
  HAVE_PRODUCTURL=" "
else
  PRODUCTURL="http://calamares.io/"
  HAVE_PRODUCTURL="#"
fi

if [ -n "$SUPPORT_URL" ] ; then
  SUPPORTURL="$SUPPORT_URL"
  HAVE_SUPPORTURL=" "
elif [ -n "$BUG_REPORT_URL" ] ; then
  SUPPORTURL="$BUG_REPORT_URL"
  HAVE_SUPPORTURL=" "
else
  SUPPORTURL="http://calamares.io/bugs/"
  HAVE_SUPPORTURL="#"
fi

cat >%{_datadir}/calamares/branding/auto/branding.desc <<EOF
# THIS FILE IS AUTOMATICALLY GENERATED! ANY CHANGES TO THIS FILE WILL BE LOST!
---
componentName:  auto

strings:
    productName:         "$NAME"
    shortProductName:    "$NAME"
    version:             "$VERSION"
    shortVersion:        "$VERSION_ID"
    versionedName:       "$NAME $VERSION"
    shortVersionedName:  "$NAME $VERSION_ID"
    bootloaderEntryName: "$NAME"
$HAVE_PRODUCTURL   productUrl:          "$PRODUCTURL"
$HAVE_SUPPORTURL   supportUrl:          "$SUPPORTURL"
#   knownIssuesUrl:      "http://calamares.io/about/"
#   releaseNotesUrl:     "http://calamares.io/about/"

images:
    productLogo:         "$LOGO"
    productIcon:         "$SPRITE"

slideshow:               "show.qml"

style:
    sidebarBackground:   "#292F34"
    sidebarText:         "#FFFFFF"
    sidebarTextSelect:   "#292F34"
EOF

%files
%doc LICENSE AUTHORS
%{_bindir}/calamares
%dir %{_datadir}/calamares/
%{_datadir}/calamares/settings.conf
%dir %{_datadir}/calamares/branding/
%{_datadir}/calamares/branding/default/
%dir %{_datadir}/calamares/branding/auto/
%ghost %{_datadir}/calamares/branding/auto/branding.desc
%{_datadir}/calamares/branding/auto/show.qml
%{_datadir}/calamares/branding/auto/lang/
%{_datadir}/calamares/modules/
%exclude %{_datadir}/calamares/modules/webview.conf
%{_datadir}/calamares/qml/
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
%exclude %{_libdir}/calamares/modules/webview/

%files webview
%{_datadir}/calamares/modules/webview.conf
%{_libdir}/calamares/modules/webview/

%files devel
%{_includedir}/libcalamares/
%{_libdir}/libcalamares.so
%{_libdir}/libcalamaresui.so
%{_libdir}/cmake/Calamares/


%changelog
* Sat Sep 26 2015 Kevin Kofler <Kevin@tigcc.ticalc.org> - 1.1.3-1
- Update to 1.1.3
- Add additional changes to calamares-default-settings.patch
- BuildRequires: qt5-qtwebkit-devel >= 5.3 for the webview module
- Add webview subpackage for the webview module (not used by default, extra dep)

* Thu Aug 27 2015 Jonathan Wakely <jwakely@redhat.com> - 1.1.2-2
- Rebuilt for Boost 1.59

* Mon Aug 17 2015 Kevin Kofler <Kevin@tigcc.ticalc.org> - 1.1.2-1
- Update to 1.1.2 (#1246955)
- Add Requires: gdisk (for sgdisk), dmidecode, upower, NetworkManager
- Add slideshow translations (fr, de, it)
- Drop obsolete calamares-1.0.1-fix-version.patch
- Rebase calamares-default-settings.patch

* Wed Aug 05 2015 Jonathan Wakely <jwakely@redhat.com> 1.0.1-6.20150502gita70306e54f505
- Rebuilt for Boost 1.58

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.1-5.20150502gita70306e54f505
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sun May 03 2015 Kevin Kofler <Kevin@tigcc.ticalc.org> - 1.0.1-4.20150502gita70306e54f505
- New snapshot, fixes bugs, improves EFI support, UI and translations
- Drop fix-reboot patch, fixed upstream
- Update default-settings patch
- Update automatic branding generation scriptlet

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 1.0.1-3
- Rebuilt for GCC 5 C++11 ABI change

* Thu Feb 05 2015 Kevin Kofler <Kevin@tigcc.ticalc.org> - 1.0.1-2
- Fix the version number reported in the About dialog (1.0.1, not 1.0.0)
- Apply upstream fix to make "Restart now" in "Finished" page actually reboot
- Make the link in the default show.qml clickable

* Mon Feb 02 2015 Kevin Kofler <Kevin@tigcc.ticalc.org> - 1.0.1-1
- Update to the official release 1.0.1 (adds slideshow support, "Finished" page)
- Install a show.qml with a default, Calamares-branded slideshow
- BuildRequires:  qt5-qtdeclarative-devel >= 5.3 (needed for the new slideshow)

* Mon Jan 19 2015 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0.17.0-8.20150119git5c6a302112cee
- New snapshot, fixes swap fstab entries and yum/dnf package removal

* Sun Jan 11 2015 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0.17.0-7.20150105gitfe44633e0ca52
- Rebuild for new extra-cmake-modules (to verify that it still builds)

* Sat Jan 10 2015 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0.17.0-6.20150105gitfe44633e0ca52
- New snapshot, improves the partitioning interface and updates translations
- Point URL to http://calamares.io/
- default-settings patch: Enable the packages module, make it remove calamares
- desktop-file patch: Remove the NoDisplay=true line, unneeded with the above
- Requires: dnf or yum depending on the Fedora version, for the packages module

* Sun Dec 07 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0.17.0-5.20141206giteb748cca8ebfc
- Bump Release to distinguish official F21 update from Copr build

* Sun Dec 07 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0.17.0-4.20141206giteb748cca8ebfc
- New snapshot, fixes detection and setup of display managers
- default-settings patch: Don't delist non-sddm DMs from displaymanager.conf
- Drop the Requires: sddm, no longer needed (now works with any DM or even none)

* Sat Dec 06 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0.17.0-3.20141206git75adfa03fcba0
- New snapshot, fixes some bugs, adds partial/incomplete grub-efi support
- Add ExclusiveArch matching the livearches from anaconda.spec (#1171380)
- Requires: grub-efi on x86_64
- Rebase default-settings patch, set efiBootloaderId in grub.cfg

* Sat Nov 29 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0.17.0-2.20141128giteee54241d1f58
- New snapshot, sets the machine-id, fixes mounting/unmounting bugs
- Rebase default-settings patch

* Thu Nov 27 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0.17.0-1.20141127git8591dcf731cbf
- New snapshot, adds locale selector, fixes installation with SELinux enabled
- Use the version number from CMakeLists.txt, now at 0.17.0
- Use post-release snapshot numbering, milestone 0.17 was already reached

* Mon Nov 24 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0-0.17.20141123gitc17898a6501fd
- New snapshot, adds "About" dialog and improves partitioning error reporting

* Thu Nov 20 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0-0.16.20141119git01c3244396f35
- Automatically generate the branding to use by default (new "auto" branding)
- Remove README.branding, no longer needed

* Thu Nov 20 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0-0.15.20141119git01c3244396f35
- New snapshot, creates /etc/default/grub if missing (calamares#128)
- README.branding: Mention new bootloaderEntryName setting
- Remove no longer needed workaround that wrote /etc/default/grub in %%post

* Tue Nov 18 2014 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0-0.14.20141117gitdf47842fc7a03
- New snapshot, makes Python modules get branding information from branding.desc
- README.branding: Update with the resulting simplified instructions

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
