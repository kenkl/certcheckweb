from flask import Flask, request, render_template
from datetime import datetime
import check_cert, json, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from buildsites import buildserverlist, add_endpoint, del_endpoint
from config import secrets

SECUREEMAIL = secrets['secureemail']
THRESHOLD = secrets['threshold']
MYEMAIL = secrets['myemail']
HOST = secrets['emailhost']
EMAILPORT = secrets['emailport']
TO = secrets['toemail']
PASSWORD = secrets['password']
LISTURL = secrets['listurl']

app = Flask(__name__)

@app.route('/')
def default_page():
    return render_template('top.html')

@app.route('/web')
def ccw():
    websites = buildserverlist()
    websites = check_cert.insert_details(websites)
    return render_template('index.html', websites=websites)

@app.route('/email')
def email():
    now=datetime.now()
    #prettydt = now.strftime('%Y-%m-%d') + '@' + now.strftime('%H:%M')
    prettydt = now.strftime('%Y-%m-%d')
    report = ''
    expcount = 0
    longestname = 0
    websites = buildserverlist()
    websites = check_cert.insert_details(websites)

    # First, let's iterate through the names to figure out which one is the longest
    for site in websites:
        thissite = site['url'] + ':' + str(site['port'])
        if len(thissite) > longestname:
            longestname = len(thissite)

    # With the longest name in hand, iterate through again to prettyprint the list
    for site in websites:
        thissite = site['url'] + ':' + str(site['port'])
        space = ' ' * (longestname - len(thissite)) # build padding based on name/port length
        if site['days_left'] <= THRESHOLD: 
            report += thissite + space + '  -  ' + str(site['days_left']) + ' days remaining\n'
            expcount += 1
    
    # Build the email body based on the list we just assembled or a congratulations if we're at 0 this time.
    if expcount > 0:
        subject=f'Certificates expiring soon ({prettydt})'
        prefix=f'The following {expcount} certificates are expiring within {THRESHOLD} days:\n\n'
        text = prefix + report + "\n\nThe full list is available at " + LISTURL
        html = """\
        <!doctype html>
        <html lang="en">
        <body style="background-color: white">
            <p style="color: black">
        """
        html += prefix
        html += """\
            </p>
            <p style="font-family: courier; color:black"><pre>
        """
        html += "<br>" + report
        html += """\
            </pre>
            </p>
            <p>The full server/cert list is available <a href="
        """
        html += LISTURL
        html += """\
        ">here</a>.</p>
        </body>
        </html>
        """
    else:
        subject=f'No certificates expiring soon ({prettydt})'
        prefix=f'Good news!! No certificates in the watchlist are expiring within {THRESHOLD} days. Congrats!\n\n'
        text = prefix + "\n\nThe full list is available at " + LISTURL
        html = """\
        <!doctype html>
        <html lang="en">
        <body style="background-color: white">
            <p style="color: black">
        """
        html += prefix
        html += """\
            </p>
            <p>The full server/cert list is available <a href="
        """
        html += LISTURL
        html += """\
        ">here</a>.</p>
        </body>
        </html>
        """

    # Now that the email's been assembled, build the MIMEMultipart message...
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = MYEMAIL
    message["To"] = TO
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    # ...and send it 
    with smtplib.SMTP(HOST, EMAILPORT) as connection:
        if SECUREEMAIL:
            connection.starttls()
            connection.login(MYEMAIL, PASSWORD)
        connection.sendmail(MYEMAIL, TO, msg=message.as_string())
    
    return render_template('emailsent.html')
        
@app.route('/dump')
def dump():
    websites = buildserverlist()
    websites = check_cert.insert_details(websites)

    resp = app.make_response(json.dumps(websites))
    resp.mimetype = 'application/json'
    return resp

@app.route('/add')
def add_host():
    host = request.args.get('host', type=str)
    port = request.args.get('port', type=int)

    if not host or not port:
        return render_template('addform.html')
        #return 'Malformed request - need host AND port'
    else:
        message = add_endpoint(host, port)
        return render_template('dbdone.html')

        #return message

@app.route('/del')
def del_host():
    host = request.args.get('host', type=str)
    port = request.args.get('port', type=int)

    if not host or not port:
        return render_template('delform.html')
        #return 'malformed request - need host AND port'
    else:
        message = del_endpoint(host, port)
        return render_template('dbdone.html')
        #return message

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
