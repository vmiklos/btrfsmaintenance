#
# spec file for package btrfsmaintenance
#
# Copyright (c) 2014 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#


Name:           btrfsmaintenance
Version:        0.1
Release:        0
Summary:        Scripts for btrfs periodic maintenance tasks
License:        GPL-2.0
Group:          System/Base
Source0:        %{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch
Recommends:     cron
Requires:       zypp-plugin-python
Requires:       libzypp(plugin:commit) = 1
%if 0%{?suse_version} >= 1210
BuildRequires:  systemd
%endif
%{?systemd_requires}
Supplements:    btrfsprogs

%description
Scripts for btrfs maintenance tasks like periodic scrub, balance, trim or defrag
on selected mountpoints or directories.

%prep
%setup -q

%build

%install
# fix build error on openSUSE and SLE
mkdir -p %{buildroot}%{_sysconfdir}/cron.daily/
mkdir -p %{buildroot}%{_sysconfdir}/cron.weekly/
mkdir -p %{buildroot}%{_sysconfdir}/cron.monthly/

install -m 755 -d %{buildroot}/usr/share/%{name}
install -m 755 btrfs-defrag.sh %{buildroot}/usr/share/%{name}
install -m 755 btrfs-balance.sh %{buildroot}/usr/share/%{name}
install -m 755 btrfs-scrub.sh %{buildroot}/usr/share/%{name}
install -m 755 btrfs-trim.sh %{buildroot}/usr/share/%{name}
install -m 755 btrfsmaintenance-refresh-cron.sh %{buildroot}/usr/share/%{name}

%if 0%{?suse_version} >= 1210
install -m 755 -d %{buildroot}%{_unitdir}
install -m 644 -D btrfsmaintenance-refresh.service %{buildroot}%{_unitdir}
install -m 755 -d %{buildroot}%{_sbindir}
ln -s /usr/sbin/service %{buildroot}%{_sbindir}/rcbtrfsmaintenance-refresh
%else
# just a hack, but sufficient
install -m 755 -d %{buildroot}/etc/cron.hourly
ln -s /usr/share/%{name}/btrfsmaintenance-refresh-cron.sh %{buildroot}/etc/cron.hourly/
%endif

install -m 755 -d %{buildroot}/usr/lib/zypp/plugins/commit
install -m 755 -D btrfs-defrag-plugin.py %{buildroot}/usr/lib/zypp/plugins/commit

install -m 755 -d %{buildroot}%{_localstatedir}/adm/fillup-templates
install -m 644 -D sysconfig.btrfsmaintenance %{buildroot}%{_localstatedir}/adm/fillup-templates

%post
%{fillup_only btrfsmaintenance}
%if 0%{?suse_version} >= 1210
%service_add_post btrfsmaintenance-refresh.service
%endif

%if 0%{?suse_version} >= 1210
%pre
%service_add_pre btrfsmaintenance-refresh.service

%preun
%service_del_preun btrfsmaintenance-refresh.service
/usr/share/%{name}/btrfsmaintenance-refresh-cron.sh uninstall

%postun
%service_del_postun btrfsmaintenance-refresh.service
%endif

%if 0%{?suse_version} < 1210
%preun
/usr/share/%{name}/btrfsmaintenance-refresh-cron.sh uninstall
%endif

%files
%defattr(-,root,root)
%{_localstatedir}/adm/fillup-templates/sysconfig.btrfsmaintenance
%dir /usr/share/%{name}
/usr/share/%{name}/*
%dir /usr/lib/zypp/
%dir /usr/lib/zypp/plugins
%dir /usr/lib/zypp/plugins/commit
/usr/lib/zypp/plugins/commit/btrfs-defrag-plugin.py
%if 0%{?suse_version} >= 1210
%dir %{_unitdir}
%{_unitdir}/btrfsmaintenance-refresh.service
%{_sbindir}/rcbtrfsmaintenance-refresh
%else
/etc/cron.hourly/btrfsmaintenance-refresh-cron.sh
%endif

%changelog