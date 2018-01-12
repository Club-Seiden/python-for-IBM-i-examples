#!/usr/bin/env python3
import argparse
import os
from itoolkit import *
from itoolkit.lib.ilibcall import *
import ibm_db_dbi as db2
import shutil

#########################################################################
#                                                                       #
# Issues                                                                #
#                                                                       #
# Using SQL to create an HTTP Server Instance does not work properly.   #
# The `mod_info_query` does not have any effect, so the new HTTP Server #
# does not point at the correct httpd.conf                              #
#                                                                       #
#########################################################################

# TODO - The instance still isn't working when starting out of the box. it times out
# TODO - zendsvr6 and apache configs have not been tested yet
# TODO - Qzui APIs would be preferable for creating and deleting HTTP Apache Instances


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


;Usage of this configuration requires following PASE and DG1 PTFs
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


def get_req_all(s):
    un = os.uname()
    version = (int(un.version), int(un.release))
    if version > (7, 1):
        return 'Require all ' + s
    else:
        if s == 'granted':
            return '''order allow,deny
allow from all'''
        else:
            return '''order deny,allow
deny from all'''


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
    {2}   
</Directory>

<Directory /www/{1}/htdocs>
    Options FollowSymLinks 
    {3}
    AllowOverride all
</Directory>

IncludeOptional /www/{1}/conf/apache-sites/*.conf
'''.format(port, name, get_req_all('denied'), get_req_all('granted'))


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
    {2}
</Directory>

<Directory /www/{1}/htdocs>
    Options FollowSymLinks 
    {3}
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
'''.format(port, name, get_req_all('denied'), get_req_all('granted'))


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
    {2}    
</Directory>

<Directory /www/{1}/htdocs>
    Options FollowSymLinks 
    {3}
    AllowOverride all
</Directory>

#XML Toolkit http settings
ScriptAlias /cgi-bin/ /QSYS.LIB/zendphp7.LIB/
<Directory /QSYS.LIB/zendphp7.LIB/>
    AllowOverride None
    {3}
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
'''.format(port, name, get_req_all('denied'), get_req_all('granted'))


def get_example_vhost_conf(name, port):
    return '''<VirtualHost *:{0}>
    ServerName {1}.domain.com
    DocumentRoot /www/{1}/example-project/htdocs

    <Directory "/www/{1}/example-project/htdocs">
        Options Indexes FollowSymLinks
        {2}
        AllowOverride All
        DirectoryIndex index.php index.html
    </Directory>


    ErrorLog "/www/{1}/example-project/logs/error_log"
    CustomLog "/www/{1}/example-project/logs/access_log" common
</VirtualHost>
'''.format(port, name, get_req_all('granted'))


def create(name, conf, port):
    path = '/www/' + name
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
        print('conf: ' + conf)
        print('name: ' + name)
        print('port: ' + port)
        os.mkdir(path)
        os.mkdir(path + '/conf')
        os.mkdir(path + '/logs')
        os.mkdir(path + '/htdocs')
        index_file = open(path + '/htdocs/index.html', "w+")
        index_file.write(get_index_html(name))

        with open(path + '/conf/fastcgi.conf', "w+") as file:
            file.write(get_fastcgi_conf(name))
        with open(path + '/conf/fastcgi.conf.twn', "w+") as file:
            file.write(get_fastcgi_conf_twn(name))
        with open(path + '/conf/fastcgi_dynamic.conf', "w+") as file:
            file.write(get_fastcgi_dynamic_conf(name))
        with open(path + '/conf/fastcgi_http_add.conf', "w+") as file:
            file.write(get_fastcgi_http_add_conf(name))

        get_conf = globals()['get_{}_conf'.format(conf)]
        with open(path + '/conf/httpd.conf', "w+") as conf_file:
            conf_file.write(get_conf(name, port))

        os.mkdir(path + '/conf/apache-sites')
        os.mkdir(path + '/example-project')
        os.mkdir(path + '/example-project/conf')
        with open("{}/example-project/conf/{}.conf".format(path, name), "w+") as file:
            file.write(get_example_vhost_conf(name, port))
        os.mkdir(path + '/example-project/htdocs')
        with open(path + '/example-project/htdocs/index.html', "w+") as file:
            file.write(get_index_html('Example Project'))
        os.mkdir(path + '/example-project/logs')
        os.symlink(
            "{}/example-project/conf/{}.conf".format(path, name),
            path + '/conf/apache-sites/example-project.conf'
        )

        # create_with_qzui_api(name)
        create_with_sql(name)


# Hopefully to go away in favor of create_with_qzui_api
def create_with_sql(name):
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
def create_with_qzui_api(name):
    itransport = iLibCall()
    itool = iToolKit()

    itool.add(iCmd('addlible', 'addlible QHTTPSVR'))
    itool.add(
        iSrvPgm('QzuiCreateInstance', 'QZHBCONF', 'QzuiCreateInstance',
                iopt={'lib': 'QHTTPSVR'})  # This doesn't seem to work, thus the ADDLIBLE above
            .addParm(iData('instance', '10a', name.upper()))
            .addParm(
                iDS('INSD0110', {'len': 'buflen'})
                    .addData(iData('autostart', '10a', '*NO'))
                    .addData(iData('threads', '10i0', '0'))
                    .addData(iData('ccsid', '10i0', '37'))
                    .addData(iData('out_table_name', '10a', '*GLOBAL'))
                    .addData(iData('out_table_lib', '10a', '*GLOBAL'))
                    .addData(iData('in_table_name', '10a', '*GLOBAL'))
                    .addData(iData('in_table_lib', '10a', '*GLOBAL'))
                    .addData(iData('config_file', '512a', '/www/' + name.lower() + '/httpd.conf'))
                    .addData(iData('server_root', '512a', '/www/' + name.lower()))
            )
            .addParm(iData('bufsize', '10i0', '', {'setlen': 'buflen'}))
            .addParm(iData('format', '10a', 'INSD0110'))
            .addParm(
                iDS('qus_ec_t', {'len': 'errlen'})
                    .addData(iData('provided', '10i0', '', {'setlen': 'errlen'}))
                    .addData(iData('available', '10i0', ''))
                    .addData(iData('msgid', '7A', ''))
                    .addData(iData('reserved', '1A', ''))
                    # These are defined specifically for CPF3C1D
                    .addData(iData('parameter', '10i0', ''))
                    .addData(iData('parmlen', '10i0', ''))
                    .addData(iData('minlen', '10i0', ''))
                    .addData(iData('maxlen', '10i0', ''))
            )
    )

    itool.call(itransport)

    result = itool.dict_out('QzuiCreateInstance')
    # print(result)
    err = result['qus_ec_t']
    if int(err['available']):
        if err['msgid'] == 'CPF3C1D':
            print("{4}: The length of {0} for parameter {1} is not valid. Values for this parameter must be greater than {2} and less than {3}.".format(
                    err['parmlen'], err['parameter'], err['minlen'], err['maxlen'], err['msgid']))
        else:
            print(err['msgid'])


def delete_with_qzui_api(name):
    print('delete')
    # Use QzuiDeleteInstance to delete HTTP Server Instance


def delete_with_sql(name):
    conn = db2.connect()
    cur = conn.cursor()

    sys_cmd = 'RMVM FILE(QUSRSYS/QATMHINSTC) MBR({})'.format(name)
    crt_http_svr = "call qcmdexc('{}');".format(sys_cmd)
    cur.execute(crt_http_svr)

    conn.commit()
    cur.close()
    conn.close()


def rename(name, newname):
    print('rename')
    # Could not find a command for this one. Only idea is to use CHGPF or some command to change the member name
    # rerun command to update update apache configuration path
    # Then mv directory to rename directory


def rename_with_sql(name, newname):
    conn = db2.connect()
    cur = conn.cursor()

    sys_cmd = 'RNMM FILE(QUSRSYS/QATMHINSTC) MBR({}) NEWMBR({})'.format(name, newname)
    crt_http_svr = "call qcmdexc('{}');".format(sys_cmd)
    cur.execute(crt_http_svr)

    query = 'create or replace alias QUSRSYS.QATMHINSTC_{0} for QUSRSYS.QATMHINSTC({0})'.format(newname)
    cur.execute(query)

    query = '''update QUSRSYS.QATMHINSTC_{0}
set CHARFIELD = '-apache -d /www/{0} -f conf/httpd.conf -AutoStartN' with NC'''.format(newname)
    cur.execute(query)

    conn.commit()
    cur.close()
    conn.close()


def start(name):
    os.system("system 'STRTCPSVR SERVER(*HTTP) HTTPSVR(" + name.upper() + ")'")


def restart(name):
    os.system("system 'STRTCPSVR SERVER(*HTTP) RESTART(*HTTP) HTTPSVR(" + name.upper() + ")'")


def stop(name):
    os.system("system 'ENDTCPSVR SERVER(*HTTP) HTTPSVR(" + name.upper() + ")'")


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

    p_delete = sp.add_parser('delete', help='Delete HTTP Server Instance')
    p_delete.add_argument('--name', '-n', required=True)
    p_delete.add_argument('--force', '-f', action='store_true', default=False)

    p_start = sp.add_parser('start', help='Start HTTP Server Instance')
    p_start.add_argument('--name', '-n', required=True)

    p_restart = sp.add_parser('restart', help='Restart HTTP Server Instance')
    p_restart.add_argument('--name', '-n', required=True)

    p_stop = sp.add_parser('stop', help='Stop HTTP Server Instance')
    p_stop.add_argument('--name', '-n', required=True)

    args = p.parse_args()

    if args.command == 'create':
        create(args.name, args.conf, args.port)
    elif args.command == 'rename':
        rename_with_sql(args.name, args.newname)
    elif args.command == 'delete':
        if args.force:
            delete_with_sql(args.name)
        else:
            verification_text = 'Are you sure you want to delete {}? This cannot be undone. (y/N) '.format(args.name)
            verified = input(verification_text) or 'n'

            if verified.lower() in ['y', 'yes']:
                delete_with_sql(args.name)
    elif args.command == 'start':
        start(args.name)
    elif args.command == 'restart':
        restart(args.name)
    elif args.command == 'stop':
        stop(args.name)


if __name__ == '__main__':
    main()
