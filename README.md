#  certcheckweb

One of the tasks in my day-job is requesting/renewing TLS/SSL certs for HTTPS endpoints. These are frequently API endpoints, used by _whatever_ other service/site needs whatever they expose. As a result, human eyes do not frequently look at them with a browser, so certificate expirations have been known to happen in such a way as to go unnoticed until someone's API breaks (because of the expired cert). Awkward.

After discussing this occasional situation with a friend/colleague (shoutout to CB), he crafted some primitive demo code, using Flask, to think about a way to monitor endpoints. I've spent a bit of time crafting refinements (the original samples didn't understand [SNI](https://en.wikipedia.org/wiki/Server_Name_Indication), leading to confusing results), getting the code to use a MySQL/MariaDB backend for the endpoint list (it was originally a static list), externalizing DB/email credentials (see config.py), added methods (functions) to maintain the endpoint list, send an email with a list of certs "expiring soon", and so forth. I then wrapped the whole thing up in a Docker image, making deployment super-simple ('docker-compose up --build -d').

Once deployed, the container is a basic Flask-hosted site with a few interesting endpoints:

```
         / (root) - a very basic landing-page (from templates/top.html)
         /web - (exposed on the root page) does a real-time sweep of the endpoints and produces a report
                of them, and their certificate expirations/issuers
         /dump - (exposed by the other link above) produces a JSON dump of the same set of endpoints. This could
                 be used to feed another process (Sharepoint?) with live data.
         /add - presents a form to add an endpoint to the list
         /del - presents a form to remove/delete an endpoint from the list
         (note: for both /add and /del - both the hostname and port are required.)
         /email - run a scan, and send an email to alert on certs that are nearing expiration
```

In practice, add/del/web serve to present a basic web-interface to manage the endpoint list stored in the SQL backend. /dump was added as an experiment - could we pull data from this thing, feeding something else (like Sharepoint) using PowerShell? The answer to that seems to be yes.

The real utility of certcheckweb is to periodically scan through the list of endpoints and send an email to the admin team (or whomever) if certs are expiring within a certain number of days (configurable in config.py).

There's a bunch I could prattle on about here (what does 'secureemail' in config.py mean?), but this project is more about creating a tool for me (and my team), and less about crafting a polished product for widespread use. As such, I'm not going to craft a Wall of Words™ "Admin Guide" - see the code to puzzle out the details, or feel free to raise an issue if you've any questions.


2021-10-29:

- initial release

2021-11-12:

- Corrected the Subject line creation for /email calls. Moving from SMTPLib to MIMEMultipart changes what _needs_ to be in that string.

2022-04-07:

- Add 'ORDER BY' to sort the scan report by server name (hostname).
