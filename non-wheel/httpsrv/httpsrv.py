#!/usr/bin/env python3
import argparse
import os
# import config
# from itoolkit import *
import ibm_db_dbi as db2

#########################################################################
#                                                                       #
# Issues                                                                #
#                                                                       #
# Using SQL to create an HTTP Server Instance does not work properly.   #
# The `mod_info_query` does not have any effect, so the new HTTP Server #
# does not point at the correct httpd.conf                              #
#                                                                       #
#########################################################################


def get_index_html(name):
    return '''<!doctype html>
<html class="no-js" lang="">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="x-ua-compatible" content="ie=edge">
        <title>{0} Works</title>
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    </head>
    <body>
        <h1>{0} works!!!</h1>
    </body>
</html>
'''.format(name)


def get_fastcgi_conf(name):
    return '''; Static PHP servers for default user
Server type="application/x-httpd-php" CommandLine="/usr/local/zendphp7/bin/php-cgi.bin" StartProcesses="1" SetEnv="LIBPATH=/usr/local/zendphp7/lib" SetEnv="PHPRC=/usr/local/zendphp7/etc/" SetEnv="PHP_FCGI_CHILDREN=10" SetEnv="PHP_FCGI_MAX_REQUESTS=0" ConnectionTimeout="30" RequestTimeout="60" SetEnv="CCSID=1208" SetEnv="LANG=C" SetEnv="INSTALLATION_UID=100313092679" SetEnv="LDR_CNTRL=MAXDATA=0x40000000" SetEnv="ZEND_TMPDIR=/usr/local/zendphp7/tmp" SetEnv="TZ=<EST>5<EDT>,M3.2.0,M11.1.0"

; Where to place socket files
IpcDir /www/{}/logs
'''.format(name)


def get_fastcgi_conf_twn(name):
    return '''; Static PHP servers for default user
Server type="application/x-httpd-php" CommandLine="/usr/local/zendphp7/bin/php-cgi.bin" StartProcesses="1" SetEnv="LIBPATH=/usr/local/zendphp7/lib" SetEnv="PHPRC=/usr/local/zendphp7/etc/" SetEnv="PHP_FCGI_CHILDREN=10" SetEnv="PHP_FCGI_MAX_REQUESTS=0" ConnectionTimeout="30" RequestTimeout="60" SetEnv="CCSID=1208" SetEnv="LANG=C" SetEnv="INSTALLATION_UID=100313092679" SetEnv="LDR_CNTRL=MAXDATA=0x40000000" SetEnv="ZEND_TMPDIR=/usr/local/zendphp7/tmp" SetEnv="TZ=<EST>-5"

; Where to place socket files
IpcDir /www/{}/logs    
'''.format(name)


def get_fastcgi_dynamic_conf(name):
    return '''; Static PHP servers for default user
DynamicServer type="application/x-httpd-php" MinProcesses=5 MaxProcesses=100 CommandLine="/usr/local/zendphp7/bin/php-cgi.bin" SetEnv="LIBPATH=/usr/local/zendphp7/lib" SetEnv="PHPRC=/usr/local/zendphp7/etc/" SetEnv="PHP_FCGI_CHILDREN=1" SetEnv="PHP_FCGI_MAX_REQUESTS=0" ConnectionTimeout="60" RequestTimeout="60" SetEnv="CCSID=1208" SetEnv="LANG=en_US" SetEnv="INSTALLATION_UID=100313092679" SetEnv="LDR_CNTRL=MAXDATA=0x40000000" SetEnv="TZ=<EST>5<EDT>,M3.2.0,M11.1.0"

; Where to place socket files
IpcDir /www/{}/logs

;Minimum and Maximum of dynamic servers
MinDynamicServers 5
MaxDynamicServers 100


;Usage of this configuration requires follwoing PASE and DG1 PTFs
;PASE PTFs
;V5R4: SI43218
;V6R1: SI43243
;V7R1: SI43244

;DG1 PTFs
;V5R4: SI43221
;V6R1: SI43224
;V7R1: SI43222
'''.format(name)


def get_fastcgi_http_add_conf(name):
    return '''Include /www/{}/conf/apache-sites 
'''.format(name)


def get_apache_conf(name, port):
    return '''# Apache Default server configuration
LoadModule proxy_module /QSYS.LIB/QHTTPSVR.LIB/QZSRCORE.SRVPGM
LoadModule proxy_http_module /QSYS.LIB/QHTTPSVR.LIB/QZSRCORE.SRVPGM
LoadModule proxy_connect_module /QSYS.LIB/QHTTPSVR.LIB/QZSRCORE.SRVPGM
LoadModule proxy_ftp_module /QSYS.LIB/QHTTPSVR.LIB/QZSRCORE.SRVPGM
LoadModule zend_enabler_module /QSYS.LIB/QHTTPSVR.LIB/QZFAST.SRVPGM

# zend fastcgi
AddType application/x-httpd-php .php
AddHandler fastcgi-script .php

# General setup directives
Listen *:{0}
HotBackup Off
HostNameLookups Off
UseCanonicalName On
TimeOut 30000
KeepAlive On
KeepAliveTimeout 5
DocumentRoot /www/{1}/htdocs
AddLanguage en .en

# protection (Basic)
<Directory />
   Order Deny,Allow 
   Deny From all     
</Directory>

<Directory /www/{1}/htdocs>
  Options FollowSymLinks 
  order allow,deny
  allow from all
  AllowOverride all
</Directory>

IncludeOptional /www/{1}/conf/apache-sites/*.conf
'''.format(port, name)


def get_zendsvr6_conf(name, port):
    return '''LoadModule proxy_module /QSYS.LIB/QHTTPSVR.LIB/QZSRCORE.SRVPGM
LoadModule proxy_http_module /QSYS.LIB/QHTTPSVR.LIB/QZSRCORE.SRVPGM
LoadModule proxy_connect_module /QSYS.LIB/QHTTPSVR.LIB/QZSRCORE.SRVPGM
LoadModule proxy_ftp_module /QSYS.LIB/QHTTPSVR.LIB/QZSRCORE.SRVPGM
LoadModule zend_enabler_module /QSYS.LIB/QHTTPSVR.LIB/QZFAST.SRVPGM
DefaultFsCCSID 37 
CGIJobCCSID 37

Listen *:{0}
DocumentRoot /www/{1}/htdocs
DirectoryIndex index.php index.html

Options -ExecCGI -FollowSymLinks -SymLinksIfOwnerMatch -Includes -IncludesNoExec -Indexes -MultiViews
LogFormat "%h %l %u %t \\"%r\\" %>s %b \\"%{{Referer}}i\\" \\"%{{User-Agent}}i\\"" combined
LogFormat "%{{Cookie}}n \\"%r\\" %t" cookie
LogFormat "%{{User-agent}}i" agent
LogFormat "%{{Referer}}i -> %U" referer
LogFormat "%h %l %u %t \\"%r\\" %>s %b" common
CustomLog logs/access_log combined
SetEnvIf "User-Agent" "Mozilla/2" nokeepalive
SetEnvIf "User-Agent" "JDK/1\.0" force-response-1.0
SetEnvIf "User-Agent" "Java/1\.0" force-response-1.0
SetEnvIf "User-Agent" "RealPlayer 4\.0" force-response-1.0
SetEnvIf "User-Agent" "MSIE 4\.0b2;" nokeepalive
SetEnvIf "User-Agent" "MSIE 4\.0b2;" force-response-1.0

TimeOut 30000
KeepAlive On
KeepAliveTimeout 5
HotBackup Off

#AddCharset UTF-8       .utf8
#AddCharset utf-8       .utf8
#AddCharset utf-7       .utf7
AddCharset UTF-8 .htm .html .xml

# zend fastcgi
AddType application/x-httpd-php .php
AddHandler fastcgi-script .php

RewriteEngine on 

<Directory />
   Order Deny,Allow 
   Deny From all     
</Directory>

<Directory /www/{1}/htdocs>
  Options FollowSymLinks 
  order allow,deny
  allow from all
  AllowOverride all
</Directory>

#XML Toolkit http settings
ScriptAlias /cgi-bin/ /QSYS.LIB/ZENDSVR6.LIB/
<Directory /QSYS.LIB/ZENDSVR6.LIB/>
    AllowOverride None
    order allow,deny
    allow from all
    SetHandler cgi-script
    Options +ExecCGI
</Directory>
#End XML Toolkit http settings

# keep access logs 10 days, error logs 10 days, FastCGI logs 10 days
LogMaint /www/{1}/logs/access_log 10 0
LogMaint /www/{1}/logs/error_log 10 0
LogMaint /www/{1}/logs/error_zfcgi 10 0

# Maintain Logs at 3 am (0 = midnight, 23 = 11 pm, etc)  
# Set for an hour when the server is active (i.e. not during an IPL or backup)  
LogMaintHour 3

IncludeOptional /www/{1}/conf/apache-sites/*.conf
'''.format(port, name)


def get_zendphp7_conf(name, port):
    return '''LoadModule proxy_module /QSYS.LIB/QHTTPSVR.LIB/QZSRCORE.SRVPGM
LoadModule proxy_http_module /QSYS.LIB/QHTTPSVR.LIB/QZSRCORE.SRVPGM
LoadModule proxy_connect_module /QSYS.LIB/QHTTPSVR.LIB/QZSRCORE.SRVPGM
LoadModule proxy_ftp_module /QSYS.LIB/QHTTPSVR.LIB/QZSRCORE.SRVPGM
LoadModule zend_enabler_module /QSYS.LIB/QHTTPSVR.LIB/QZFAST.SRVPGM
DefaultFsCCSID 37 
CGIJobCCSID 37    

Listen *:{0}
DocumentRoot /www/{1}/htdocs
DirectoryIndex index.php index.html

Options -ExecCGI -FollowSymLinks -SymLinksIfOwnerMatch -Includes -IncludesNoExec -Indexes -MultiViews
LogFormat "%h %l %u %t \\"%r\\" %>s %b \\"%{{Referer}}i\\" \\"%{{User-Agent}}i\\"" combined
LogFormat "%{{Cookie}}n \\"%r\\" %t" cookie
LogFormat "%{{User-agent}}i" agent
LogFormat "%{{Referer}}i -> %U" referer
LogFormat "%h %l %u %t \\"%r\\" %>s %b" common
CustomLog logs/access_log combined
SetEnvIf "User-Agent" "Mozilla/2" nokeepalive
SetEnvIf "User-Agent" "JDK/1\.0" force-response-1.0
SetEnvIf "User-Agent" "Java/1\.0" force-response-1.0
SetEnvIf "User-Agent" "RealPlayer 4\.0" force-response-1.0
SetEnvIf "User-Agent" "MSIE 4\.0b2;" nokeepalive
SetEnvIf "User-Agent" "MSIE 4\.0b2;" force-response-1.0

TimeOut 30000
KeepAlive On
KeepAliveTimeout 5
HotBackup Off

#AddCharset UTF-8       .utf8
#AddCharset utf-8       .utf8
#AddCharset utf-7       .utf7
AddCharset UTF-8 .htm .html .xml

# zend fastcgi
AddType application/x-httpd-php .php
AddHandler fastcgi-script .php

RewriteEngine on 

<Directory />
   Order Deny,Allow 
   Deny From all     
</Directory>

<Directory /www/{1}/htdocs>
  Options FollowSymLinks 
  order allow,deny
  allow from all
  AllowOverride all
</Directory>

#XML Toolkit http settings
ScriptAlias /cgi-bin/ /QSYS.LIB/zendphp7.LIB/
<Directory /QSYS.LIB/zendphp7.LIB/>
    AllowOverride None
    order allow,deny
    allow from all
    SetHandler cgi-script
    Options +ExecCGI
</Directory>
#End XML Toolkit http settings

# keep access logs 10 days, error logs 10 days, FastCGI logs 10 days
LogMaint /www/{1}/logs/access_log 10 0
LogMaint /www/{1}/logs/error_log 10 0
LogMaint /www/{1}/logs/error_zfcgi 10 0

# Maintain Logs at 3 am (0 = midnight, 23 = 11 pm, etc)  
# Set for an hour when the server is active (i.e. not during an IPL or backup)  
LogMaintHour 3

IncludeOptional /www/{1}/conf/apache-sites/*.conf
'''.format(port, name)


def get_example_vhost_conf(name, port):
    return '''<VirtualHost *:{0}>
    ServerName {1}.domain.com
    DocumentRoot /www/{1}/example-project/htdocs

    <Directory "/www/{1}/example-project/htdocs">
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
        DirectoryIndex index.php index.html
    </Directory>


    ErrorLog "/www/{1}/example-project/logs/error_log"
    CustomLog "/www/{1}/example-project/logs/access_log" common
</VirtualHost>
'''.format(port, name)


def create(name, conf, port):
    path = '/www/{}'.format(name)
    verification_text = '''/www/
    {0}/
        conf/
            apache-sites/
                example-vhost.conf
            httpd.conf
        example-project/
            conf/
                {0}.conf
            htdocs/
                index.html
            logs/
        htdocs/
            index.html
        logs/
'''.format(name)

    verification_text += "Does the above folder structure look correct? (Y/n) "

    verified = input(verification_text) or 'Y'

    if verified.lower() in ['y', 'yes']:
        print('conf: {}'.format(conf))
        print('name: {}'.format(name))
        print('port: {}'.format(port))
        os.mkdir('{}'.format(path))
        os.mkdir('{}/conf'.format(path))
        os.mkdir('{}/logs'.format(path))
        os.mkdir('{}/htdocs'.format(path))
        index_file = open("{}/htdocs/index.html".format(path), "w+")
        index_file.write(get_index_html(name))

        with open("{}/conf/fastcgi.conf".format(path), "w+") as file:
            file.write(get_fastcgi_conf(name))
        with open("{}/conf/fastcgi.conf.twn".format(path), "w+") as file:
            file.write(get_fastcgi_conf_twn(name))
        with open("{}/conf/fastcgi_dynamic.conf".format(path), "w+") as file:
            file.write(get_fastcgi_dynamic_conf(name))
        with open("{}/conf/fastcgi_http_add.conf".format(path), "w+") as file:
            file.write(get_fastcgi_http_add_conf(name))

        get_conf = globals()['get_{}_conf'.format(conf)]
        with open("{}/conf/httpd.conf".format(path), "w+") as conf_file:
            conf_file.write(get_conf(name, port))

        os.mkdir('{}/conf/apache-sites'.format(path))
        os.mkdir('{}/example-project'.format(path))
        os.mkdir('{}/example-project/conf'.format(path))
        with open("{}/example-project/conf/{}.conf".format(path, name), "w+") as file:
            file.write(get_example_vhost_conf(name, port))
        os.mkdir('{}/example-project/htdocs'.format(path))
        with open("{}/example-project/htdocs/index.html".format(path), "w+") as file:
            file.write(get_index_html('Example Project'))
        os.mkdir('{}/example-project/logs'.format(path))
        os.symlink(
            "{}/example-project/conf/{}.conf".format(path, name),
            "{}/conf/apache-sites/example-project.conf".format(path)
        )

        create_with_sql(name)


# Hopefully to go away in favor of create_with_qzui_api
def create_with_sql(name):
    # This connection is for the SQL way of creating an HTTP Server Instance.
    conn = db2.connect()
    cur = conn.cursor()

    sys_cmd = "CPYF FROMFILE(QUSRSYS/QATMHINSTC) TOFILE(QUSRSYS/QATMHINSTC) " +\
        "FROMMBR(APACHEDFT) TOMBR({}) MBROPT(*REPLACE)".format(name)
    crt_http_svr = "call qcmdexc('{}');".format(sys_cmd)
    cur.execute(crt_http_svr)

    query = 'create or replace alias QUSRSYS.QATMHINSTC_{0} for QUSRSYS.QATMHINSTC({0})'.format(name)
    cur.execute(query)

    query = '''update QUSRSYS.QATMHINSTC_{0}
set CHARFIELD = '-apache -d /www/{0} -f conf/httpd.conf -AutoStartN' with NC'''.format(name)
    cur.execute(query)

    conn.commit()
    cur.close()
    conn.close()


# This is the part that needs a lot of help.
# I (Josh) do not know the Python Toolkit for IBM i. I'm willing to learn.
def create_with_qzui_api():
    itool = iToolKit()
    # itool.add(
    #     iSrvPgm('qzuicrtins', 'QZUICRTINS', 'QzuiCreateInstance')
    #         .addParm(iData('name', '10a', options.devenv))
    #     # .addParm('idata', '')
    # )
    # itool.call(config.itransport)


def main():
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(title='commands', dest='command')

    p_create = sp.add_parser('create', help='Create HTTP Server Instance')
    p_create.add_argument('--conf', '-t', default="zendphp7", choices=['zendphp7', 'zendsvr6', 'apache'])
    p_create.add_argument('--name', '-n', required=True)
    p_create.add_argument('--port', '-p', required=True)

    p_rename = sp.add_parser('rename', help='Rename HTTP Server Instance')
    p_rename.add_argument('--name', '-n', required=True)
    p_rename.add_argument('--newname', '-e', required=True)

    p_rename = sp.add_parser('delete', help='Delete HTTP Server Instance')
    p_rename.add_argument('--name', '-n', required=True)

    args = p.parse_args()

    if args.command == 'create':
        if len(args.name) <= 10:
            create(args.name, args.conf, args.port)
        else:
            p.error('Name must be 10 characters or less')
    elif args.command == 'rename':
        print('rename')
    elif args.command == 'delete':
        print('delete')


if __name__ == '__main__':
    main()
