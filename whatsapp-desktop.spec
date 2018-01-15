%global __provides_exclude_from %{_libdir}/%{name}/.*\\.so
%global privlibs libffmpeg|libnode
%global __requires_exclude ^(%{privlibs})\\.so

# Oh, it fetch some binaries. Fucking nodejs
%global debug_package %{nil}

Summary:	WhatsApp desktop client, based on the official WhatsApp web app
Name:		whatsapp-desktop
Version:	0.4.2
Release:	1%{?dist}

License:	MIT
URL:		https://github.com/Enrico204/Whatsapp-Desktop
Source0:	https://github.com/Enrico204/Whatsapp-Desktop/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:	%{name}.desktop

BuildRequires:	desktop-file-utils
BuildRequires:	hicolor-icon-theme
BuildRequires:	npm >= 3.10.0
BuildRequires:	ImageMagick
BuildRequires:	chrpath

%description
This is NOT an official product. This project does not attempt to reverse
engineer the WhatsApp API or attempt to reimplement any part of the WhatsApp
client. Any communication between the user and WhatsApp servers is handled
by official WhatsApp Web itself; this is just a native wrapper for WhatsApp
Web, like a browser.

%prep
%autosetup -n Whatsapp-Desktop-%{version}

%build
# Oh, NodeJS and Yarn, what?
npm install yarn
./node_modules/yarn/bin/yarn install
./node_modules/yarn/bin/yarn run build:linux

%install
chmod -x readme.md

mkdir -p %{buildroot}%{_libdir}/%{name}

%ifarch x86_64
cp -r dist/WhatsApp-linux-x64/* %{buildroot}%{_libdir}/%{name}/
%else
cp -r dist/WhatsApp-linux-ia32/* %{buildroot}%{_libdir}/%{name}/
%endif

%if 0%{?fedora} < 27
cp -r node_modules %{buildroot}%{_libdir}/%{name}/resources/app/
rm -r %{buildroot}%{_libdir}/%{name}/resources/app/node_modules/electron
%endif

# Remove rpath
chrpath --delete %{buildroot}%{_libdir}/%{name}/WhatsApp

mkdir -p %{buildroot}%{_datadir}/applications
install -m644 %{SOURCE1} %{buildroot}%{_datadir}/applications/%{name}.desktop

desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

mkdir -p %{buildroot}%{_bindir}
for size in 16 24 32 64 128; do
    mkdir -p %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps
    convert -resize ${size}x${size} %{buildroot}%{_libdir}/%{name}/resources/app/assets/icon/icon@2x.png \
	%{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/%{name}.png
done

convert -resize 16x16 %{buildroot}%{_libdir}/%{name}/resources/app/assets/icon/icon@2x.png \
        %{buildroot}%{_libdir}/%{name}/resources/app/assets/img/trayTemplate.png

convert -resize 32x32 %{buildroot}%{_libdir}/%{name}/resources/app/assets/icon/icon@2x.png \
        %{buildroot}%{_libdir}/%{name}/resources/app/assets/img/trayTemplate@2x.png

cd %{buildroot}%{_bindir}
ln -s ../%{_lib}/%{name}/WhatsApp %{name}
cd -

mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d/

echo "%{_libdir}/%{name}" > %{buildroot}%{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf

%post
update-desktop-database &> /dev/null || :
touch --no-create /usr/share/icons/hicolor &>/dev/null || :
if [ -x /usr/bin/gtk-update-icon-cache ]; then
    /usr/bin/gtk-update-icon-cache --quiet /usr/share/icons/hicolor || :
fi

/sbin/ldconfig

%postun
if [ $1 -eq 0 ] ; then
    touch --no-create /usr/share/icons/hicolor &>/dev/null
    gtk-update-icon-cache /usr/share/icons/hicolor &>/dev/null || :
fi
update-desktop-database &> /dev/null || :

/sbin/ldconfig

%posttrans
gtk-update-icon-cache /usr/share/icons/hicolor &>/dev/null || :

%files
%doc readme.md
%config(noreplace) %{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf
%{_bindir}/%{name}
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/*
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/applications/%{name}.desktop

%changelog
* Sun Jan 14 2018 Arkady L. Shane <ashejn@russianfedora.pro> - 0.4.2-1
- update to 0.4.2
- use yarn

* Wed Nov 29 2017 Arkady L. Shane <ashejn@russianfedora.pro> - 0.3.14-2
- pack some node packages for old nodejs

* Wed Nov 29 2017 Arkady L. Shane <ashejn@russianfedora.pro> - 0.3.14-1
- update to 0.3.14

* Wed Jun  7 2017 Arkady L. Shane <ashejn@russianfedora.pro> - 0.3.3-1
- initial build
