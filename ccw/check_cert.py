import OpenSSL, ssl, socket, datetime

def get_details(url, port):
    '''Returns details of cert presented by server (url) and port'''
    details = {}
    hostname = url
    try:
        #Creating a context. We don't care about cert issuer trust or hostname matching
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as sslsock:

                der_cert = sslsock.getpeercert(True)
                pem_cert = ssl.DER_cert_to_PEM_cert(der_cert)
                x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, pem_cert)
                
                cert_expire_date_as_string = x509.get_notAfter().decode('ascii')
                cert_issuer = x509.get_issuer().CN
                #now = datetime.datetime.now()
                cert_expire_date = datetime.datetime.strptime(cert_expire_date_as_string, '%Y%m%d%H%M%SZ')
                #days_left = (cert_expire_date - now).days
                #ipaddr = socket.gethostbyname(hostname)
    except ConnectionRefusedError:
        details['expdate'] = datetime.datetime.now()
        details['issuer'] = "CONNECTION REFUSED"
        details['ipaddr'] = socket.gethostbyname(hostname)
    except socket.gaierror:
        details['expdate'] = datetime.datetime.now()
        details['issuer'] = "NAME NOT FOUND"
        details['ipaddr'] = '0.0.0.0'
    except: 
        details['expdate'] = datetime.datetime.now()
        details['issuer'] = "LOLOMGWTF"
        details['ipaddr'] = '0.0.0.0'
    else:

        details['expdate'] = cert_expire_date
        details['issuer'] = cert_issuer
        details['ipaddr'] = socket.gethostbyname(hostname)

    #return cert_expire_date
    return details

def insert_details(websites):
    '''Iterate through websites and add key/value pairs for "days_left", "ipaddr" and "issuer"'''
    for site in websites:
        now = datetime.datetime.now()
        #print(site)
        details = get_details(site['url'], site['port'])
        site['days_left'] = (details['expdate'] - now).days # .days returns just the number of days
        site['issuer'] = details['issuer']
        site['ipaddr'] = details['ipaddr']
    return websites

