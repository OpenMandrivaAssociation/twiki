%if %{_use_internal_dependency_generator}
%define __noautoprov 'perl\\((.*)\\)'
%define __noautoreq 'perl\\(TWiki(.*)\\)|perl\\(Assert\\)|perl\\(Monitor\\)'
%else
%define _provides_exceptions perl(.*)
%define _requires_exceptions perl(\\(TWiki.*\\|Assert\\|Monitor\\))

%endif

Name:       twiki
Version:    4.3.2
Release:    6
Summary:    The Open Source Enterprise Wiki and Web 2.0 Application Platform
License:    GPL
Group:      System/Servers
URL:        http://www.twiki.org
Source:     http://prdownloads.sourceforge.net/twiki/TWiki-%{version}.tgz
Requires:   apache
Requires:   rcs
BuildArch:  noarch

%description
Welcome to TWiki, a flexible, powerful, and easy to use enterprise wiki,
enterprise collaboration platform, and knowledge management system. It is a
Structured Wiki, typically used to run a project development space, a document
management system, a knowledge base, or any other groupware tool, on an
intranet or on the Internet. Web content can be created collaboratively by
using just a browser. Users without programming skills can create web
applications. Developers can extend the functionality of TWiki with Plugins.
TWiki fosters information flow within an organization, lets distributed teams
work together seamlessly and productively, and eliminates the one-webmaster
syndrome of outdated intranet content.

%prep
%setup -q -c
chmod -R u+w .
chmod 644 lib/TWiki/Plugins/TWikiNetSkinPlugin.pm

%build

%install
rm -rf %{buildroot}

# non-writable content
install -d -m 755 %{buildroot}%{_datadir}/%{name}/bin

for file in robots.txt bin/setlib.cfg; do
    install -m 644 $file %{buildroot}%{_datadir}/%{name}/bin
done

for file in attach configure changes edit login logon manage oops preview \
    rdiff rdiffauth register rename resetpasswd rest save search statistics \
    upload view viewauth viewfile; do
    install -m 755 bin/$file %{buildroot}%{_datadir}/%{name}/bin
done

cp -pr bin/logos %{buildroot}%{_datadir}/%{name}/bin/

for dir in lib locale templates tools; do
    cp -pr $dir %{buildroot}%{_datadir}/%{name}
done

# writable content
install -d -m 755 %{buildroot}%{_localstatedir}/lib/%{name}
for dir in data pub working; do
    cp -pr $dir %{buildroot}%{_localstatedir}/lib/%{name}
done

# configuration
install -d -m 755 %{buildroot}%{_sysconfdir}/%{name}
install -m 644 bin/LocalLib.cfg.txt \
    %{buildroot}%{_sysconfdir}/%{name}/LocalLib.cfg
pushd %{buildroot}%{_datadir}/%{name}/bin
ln -sf ../../../..%{_sysconfdir}/%{name}/LocalLib.cfg .
popd
perl -pi \
    -e 's|\$twikiLibPath =.*|\$twikiLibPath = "%{_datadir}/%{name}/lib";|' \
     %{buildroot}%{_sysconfdir}/twiki/LocalLib.cfg
cat > %{buildroot}%{_sysconfdir}/%{name}/LocalSite.cfg <<'EOF'
# **URL M**
#  This is the root of all TWiki URLs e.g. http://myhost.com:123.
$TWiki::cfg{DefaultUrlHost} = 'http://localhost';

# This is the 'cgi-bin' part of URLs used to access the TWiki bin
# directory
$TWiki::cfg{ScriptUrlPath} = '/twiki/bin';

# Attachments URL path e.g. /twiki/pub
$TWiki::cfg{PubUrlPath} = '/twiki/pub';

# Template directory e.g. /usr/local/twiki/templates
$TWiki::cfg{TemplateDir} = '/usr/share/twiki/templates';

# Translation files directory (file path, not URL) e.g. /usr/local/twiki/locales
$TWiki::cfg{LocalesDir} = '/usr/share/twiki/locales';

# Topic files store (file path, not URL) e.g. /usr/local/twiki/data
$TWiki::cfg{DataDir} = '/var/lib/twiki/data';

# Attachments store (file path, not URL), must match /twiki/pub e.g.
# /usr/local/twiki/pub
$TWiki::cfg{PubDir} = '/var/lib/twiki/pub';

# Directory where TWiki stores files that are required for the management
# of TWiki, but are not normally required to be browsed from the web.
$TWiki::cfg{WorkingDir} = '/var/lib/twiki/working';
EOF
pushd %{buildroot}%{_datadir}/%{name}/lib
ln -sf ../../../..%{_sysconfdir}/%{name}/LocalSite.cfg .
popd

# cleanup
rm -rf %{buildroot}%{_datadir}/%{name}/lib/CPAN
rm -f %{buildroot}%{_datadir}/%{name}/www/bin/.htaccess.txt
rm -f %{buildroot}%{_datadir}/%{name}/www/bin/configure
find %{buildroot}%{_localstatedir}/lib/%{name} -name .htaccess -o -name README \
    | xargs rm -f

# apache configuration
install -d -m 755 %{buildroot}%{_webappconfdir}
cat > %{buildroot}%{_webappconfdir}/%{name}.conf <<EOF
# Twiki Apache configuration
Alias /twiki/pub %{_localstatedir}/lib/%{name}/pub
Alias /twiki %{_datadir}/%{name}

<Directory %{_datadir}/%{name}>
    Require all granted
    DirectoryIndex bin/view
</Directory>

<Directory %{_datadir}/%{name}/bin>
    Options +ExecCGI
    SetHandler cgi-script
</Directory>

<Directory %{_datadir}/%{name}/lib>
    Require all denied
</Directory>

<Directory %{_datadir}/%{name}/locales>
    Require all denied
</Directory>

<Directory %{_datadir}/%{name}/templates>
    Require all denied
</Directory>

<Directory %{_datadir}/%{name}/tools>
    Require all denied
</Directory>

<Directory %{_localstatedir}/lib/%{name}/pub>
    Require all granted
</Directory>

EOF

%files
%doc AUTHORS COPYING COPYRIGHT LICENSE
%{_datadir}/twiki
%attr(-,apache,apache) %{_localstatedir}/lib/twiki
%config(noreplace) %{_webappconfdir}/%{name}.conf
%dir %{_sysconfdir}/%{name}
%config(noreplace) %attr(-,apache,apache) %{_sysconfdir}/%{name}/LocalSite.cfg
%config(noreplace) %attr(-,root,root) %{_sysconfdir}/%{name}/LocalLib.cfg

