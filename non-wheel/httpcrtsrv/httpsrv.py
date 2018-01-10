#!/usr/bin/env python3
import optparse
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
    return '''
<!doctype html>
<html class="no-js" lang="">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="x-ua-compatible" content="ie=edge">
        <title>%s Works</title>
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    </head>
    <body>
        <h1>%s works!!!</h1>
    </body>
</html>
''' % (name, name)

def get_fastcgi_conf(name):
    return '''; Static PHP servers for default user
Server type="application/x-httpd-php" CommandLine="/usr/local/zendphp7/bin/php-cgi.bin" StartProcesses="1" SetEnv="LIBPATH=/usr/local/zendphp7/lib" SetEnv="PHPRC=/usr/local/zendphp7/etc/" SetEnv="PHP_FCGI_CHILDREN=10" SetEnv="PHP_FCGI_MAX_REQUESTS=0" ConnectionTimeout="30" RequestTimeout="60" SetEnv="CCSID=1208" SetEnv="LANG=C" SetEnv="INSTALLATION_UID=100313092679" SetEnv="LDR_CNTRL=MAXDATA=0x40000000" SetEnv="ZEND_TMPDIR=/usr/local/zendphp7/tmp" SetEnv="TZ=<EST>5<EDT>,M3.2.0,M11.1.0"

; Where to place socket files
IpcDir /www/%s/logs
''' % name

def get_fastcgi_conf_twn(name):
    return '''; Static PHP servers for default user
Server type="application/x-httpd-php" CommandLine="/usr/local/zendphp7/bin/php-cgi.bin" StartProcesses="1" SetEnv="LIBPATH=/usr/local/zendphp7/lib" SetEnv="PHPRC=/usr/local/zendphp7/etc/" SetEnv="PHP_FCGI_CHILDREN=10" SetEnv="PHP_FCGI_MAX_REQUESTS=0" ConnectionTimeout="30" RequestTimeout="60" SetEnv="CCSID=1208" SetEnv="LANG=C" SetEnv="INSTALLATION_UID=100313092679" SetEnv="LDR_CNTRL=MAXDATA=0x40000000" SetEnv="ZEND_TMPDIR=/usr/local/zendphp7/tmp" SetEnv="TZ=<EST>-5"

; Where to place socket files
IpcDir /www/%s/logs    
''' % name

def get_fastcgi_dynamic_conf(name):
    return '''; Static PHP servers for default user
DynamicServer type="application/x-httpd-php" MinProcesses=5 MaxProcesses=100 CommandLine="/usr/local/zendphp7/bin/php-cgi.bin" SetEnv="LIBPATH=/usr/local/zendphp7/lib" SetEnv="PHPRC=/usr/local/zendphp7/etc/" SetEnv="PHP_FCGI_CHILDREN=1" SetEnv="PHP_FCGI_MAX_REQUESTS=0" ConnectionTimeout="60" RequestTimeout="60" SetEnv="CCSID=1208" SetEnv="LANG=en_US" SetEnv="INSTALLATION_UID=100313092679" SetEnv="LDR_CNTRL=MAXDATA=0x40000000" SetEnv="TZ=<EST>5<EDT>,M3.2.0,M11.1.0"

; Where to place socket files
IpcDir /www/%s/logs

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
    
''' % name

def get_fastcgi_http_add_conf(name):
    return '''Include /www/%s/conf/apache-sites 
''' % name

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
Listen *:%s
HotBackup Off
HostNameLookups Off
UseCanonicalName On
TimeOut 30000
KeepAlive On
KeepAliveTimeout 
DocumentRoot /www/%s/htdocs
AddLanguage en .en

# protection (Basic)
<Directory />
   Order Deny,Allow 
   Deny From all     
</Directory>

<Directory /www/%s/htdocs>
  Options FollowSymLinks 
  order allow,deny
  allow from all
  AllowOverride all
</Directory>

IncludeOptional /www/%s/conf/apache-sites/*.conf
''' % (port, name, name, name)


def get_zendsvr6_conf(name, port):
    return '''LoadModule proxy_module /QSYS.LIB/QHTTPSVR.LIB/QZSRCORE.SRVPGM
LoadModule proxy_http_module /QSYS.LIB/QHTTPSVR.LIB/QZSRCORE.SRVPGM
LoadModule proxy_connect_module /QSYS.LIB/QHTTPSVR.LIB/QZSRCORE.SRVPGM
LoadModule proxy_ftp_module /QSYS.LIB/QHTTPSVR.LIB/QZSRCORE.SRVPGM
LoadModule zend_enabler_module /QSYS.LIB/QHTTPSVR.LIB/QZFAST.SRVPGM
DefaultFsCCSID 37 
CGIJobCCSID 37

Listen *:%s
DocumentRoot /www/%s/htdocs
DirectoryIndex index.php index.html

Options -ExecCGI -FollowSymLinks -SymLinksIfOwnerMatch -Includes -IncludesNoExec -Indexes -MultiViews
LogFormat "%%h %%l %%u %%t \\"%%r\\" %%>s %%b \\"%%{Referer}i\\" \\"%%{User-Agent}i\\"" combined
LogFormat "%%{Cookie}n \\"%%r\\" %%t" cookie
LogFormat "%%{User-agent}i" agent
LogFormat "%%{Referer}i -> %%U" referer
LogFormat "%%h %%l %%u %%t \\"%%r\\" %%>s %%b" common
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

<Directory /www/%s/htdocs>
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
LogMaint /www/%s/logs/access_log 10 0
LogMaint /www/%s/logs/error_log 10 0
LogMaint /www/%s/logs/error_zfcgi 10 0

# Maintain Logs at 3 am (0 = midnight, 23 = 11 pm, etc)  
# Set for an hour when the server is active (i.e. not during an IPL or backup)  
LogMaintHour 3

IncludeOptional /www/%s/conf/apache-sites/*.conf
''' % (port, name, name, name, name, name, name)


def get_zendphp7_conf(name, port):
    return '''LoadModule proxy_module /QSYS.LIB/QHTTPSVR.LIB/QZSRCORE.SRVPGM
LoadModule proxy_http_module /QSYS.LIB/QHTTPSVR.LIB/QZSRCORE.SRVPGM
LoadModule proxy_connect_module /QSYS.LIB/QHTTPSVR.LIB/QZSRCORE.SRVPGM
LoadModule proxy_ftp_module /QSYS.LIB/QHTTPSVR.LIB/QZSRCORE.SRVPGM
LoadModule zend_enabler_module /QSYS.LIB/QHTTPSVR.LIB/QZFAST.SRVPGM
DefaultFsCCSID 37 
CGIJobCCSID 37    

Listen *:%s
DocumentRoot /www/%s/htdocs
DirectoryIndex index.php index.html

Options -ExecCGI -FollowSymLinks -SymLinksIfOwnerMatch -Includes -IncludesNoExec -Indexes -MultiViews
LogFormat "%%h %%l %%u %%t \\"%%r\\" %%>s %%b \\"%%{Referer}i\\" \\"%%{User-Agent}i\\"" combined
LogFormat "%%{Cookie}n \\"%%r\\" %%t" cookie
LogFormat "%%{User-agent}i" agent
LogFormat "%%{Referer}i -> %%U" referer
LogFormat "%%h %%l %%u %%t \\"%%r\\" %%>s %%b" common
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

<Directory /www/%s/htdocs>
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
LogMaint /www/%s/logs/access_log 10 0
LogMaint /www/%s/logs/error_log 10 0
LogMaint /www/%s/logs/error_zfcgi 10 0

# Maintain Logs at 3 am (0 = midnight, 23 = 11 pm, etc)  
# Set for an hour when the server is active (i.e. not during an IPL or backup)  
LogMaintHour 3

IncludeOptional /www/%s/conf/apache-sites/*.conf
''' % (port, name, name, name, name, name, name)


def get_example_vhost_conf(name, port):
    return '''
<VirtualHost *:%s>
    ServerName %s.domain.com
    DocumentRoot /www/%s/example-project/htdocs

    <Directory "/www/%s/example-project/htdocs">
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
        DirectoryIndex index.php index.html
    </Directory>


    ErrorLog "/www/%s/example-project/logs/error_log"
    CustomLog "/www/%s/example-project/logs/access_log" common
</VirtualHost>
''' % (port, name, name, name, name, name)


def create(name, conf, port):
    path = '/www/%s' % name
    verification_text = """
    /www/
        %s/
            conf/
                apache-sites/
                    example-vhost.conf
                httpd.conf
            example-project/
                conf/
                    %s.conf
                htdocs/
                    index.html
                logs/
            htdocs/
                index.html
            logs/
""" % (name, name)

    verification_text += "Does the above folder structure look correct? (Y/n) "

    verified = input(verification_text) or 'Y'

    if verified in ['y', 'Y', 'yes', 'Yes', 'YES']:
        print('conf: %s' % conf)
        print('name: %s' % name)
        print('port: %s' % port)
        os.mkdir('%s' % path)
        os.mkdir('%s/conf' % path)
        os.mkdir('%s/logs' % path)
        os.mkdir('%s/htdocs' % path)
        index_file = open("%s/htdocs/index.html" % path, "w+")
        index_file.write(get_index_html(name))

        conf_file = open("%s/conf/httpd.conf" % path, "w+")
        fastcgi_conf_file = open("%s/conf/fastcgi.conf" % path, "w+")
        fastcgi_conf_twn_file = open("%s/conf/fastcgi.conf.twn" % path, "w+")
        fastcgi_dynamic_conf_file = open("%s/conf/fastcgi_dynamic.conf" % path, "w+")
        fastcgi_http_add_conf_file = open("%s/conf/fastcgi_http_add.conf" % path, "w+")
        fastcgi_conf_file.write(get_fastcgi_conf(name))
        fastcgi_conf_twn_file.write(get_fastcgi_conf_twn(name))
        fastcgi_dynamic_conf_file.write(get_fastcgi_dynamic_conf(name))
        fastcgi_http_add_conf_file.write(get_fastcgi_http_add_conf(name))
        fastcgi_conf_file.close()
        fastcgi_conf_twn_file.close()
        fastcgi_dynamic_conf_file.close()
        fastcgi_http_add_conf_file.close()

        if conf == "apache":
            conf_file.write(get_apache_conf(name, port))
        elif conf == "zendphp7":
            conf_file.write(get_zendphp7_conf(name, port))
        elif conf == "zendsvr6":
            conf_file.write(get_zendsvr6_conf(name, port))

        conf_file.close()

        os.mkdir('%s/conf/apache-sites' % path)
        os.mkdir('%s/example-project' % path)
        os.mkdir('%s/example-project/conf' % path)
        vhost_file = open("%s/example-project/conf/%s.conf" % (path, name), "w+")
        vhost_file.write(get_example_vhost_conf(name, port))
        vhost_file.close()
        os.mkdir('%s/example-project/htdocs' % path)
        index_file = open("%s/example-project/htdocs/index.html" % path, "w+")
        index_file.write(get_index_html('Example Project'))
        index_file.close()
        os.mkdir('%s/example-project/logs' % path)
        os.symlink("%s/example-project/conf/%s.conf" % (path, name), "%s/conf/apache-sites/example-project.conf" % path)

        create_with_sql(name)


# Hopefully to go away in favor of create_with_qzui_api
def create_with_sql(name):
    # This connection is for the SQL way of creating an HTTP Server Instance.
    conn = db2.connect()
    cur = conn.cursor()

    sys_cmd = "CPYF FROMFILE(QUSRSYS/QATMHINSTC) TOFILE(QUSRSYS/QATMHINSTC) " +\
            "FROMMBR(APACHEDFT) TOMBR(%s) MBROPT(*REPLACE)" % name
    crt_http_svr = "call qcmdexc('%s');" % sys_cmd
    cur.execute(crt_http_svr)

    # This is the part that does not work properly.
    mod_info_query = '''
create or replace alias QUSRSYS.QATMHINSTC_%s for QUSRSYS.QATMHINSTC(%s);
update QUSRSYS.QATMHINSTC_%s
set CHARFIELD = '-apache -d /www/%s -f conf/httpd.conf -AutoStartN';
''' % (name, name, name, name)

    cur.execute(mod_info_query)
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
    usage = '''
    python3 httpsrv.py (-c|d|r) [--conf=<template>] [--name=<name>] [--port=<number>] [--newname=<name>]
    python3 httpsrv.py -c --conf=zendsvr6 --name=test --port=10090
    python3 httpsrv.py -r --name=test --newname=develop
    python3 httpsrv.py -d --name=develop
'''
    p = optparse.OptionParser(usage)
    p.add_option('-c', action='store_true', dest="create", help='Create HTTP Server Instance')
    p.add_option('-d', action='store_true', dest="delete", help='Delete HTTP Server Instance')
    p.add_option('-r', action='store_true', dest="rename", help='Rename HTTP Server Instance')
    p.add_option('--conf', '-t', default="zendphp7",
         help='Template to use for Apache Config. zendphp7|zendsvr6|apache [default: zendphp7]')
    p.add_option('--name', '-n', help="Name of HTTP Server Instance")
    p.add_option('--newname', '-e', help="New name for HTTP Server Instance")
    p.add_option('--port', '-p', help="Default port for HTTP Server Instance")
    options, arguments = p.parse_args()

    if len([x for x in (options.create, options.delete, options.rename) if x is not None]) != 1:
        p.error('options -c, -d, and -r cannot be used together.')

    if options.create:
        if len([x for x in (options.name, options.conf, options.port) if x is not None]) == 3:
            if options.conf in ['apache', 'zendphp7', 'zendsvr6']:
                if len(options.name) <= 10:
                    create(options.name, options.conf, options.port)
                else:
                    p.error('Name must be 10 characters or less')
            else:
                p.error('--conf=apache|zendphp7|zendsvr6')
        else:
            p.error('--name, --conf, --port are all required when creating an HTTP Server Instance')


if __name__ == '__main__':
    main()
