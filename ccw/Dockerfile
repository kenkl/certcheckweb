FROM python:3.9.2-alpine3.13
RUN apk update && apk --no-cache add tzdata python3-dev gcc libc-dev libressl-dev musl-dev libffi-dev 
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
RUN pip install --upgrade pip
RUN pip install cryptography
RUN pip install Flask pyOpenSSL mysql-connector-python
RUN cp /usr/share/zoneinfo/America/New_York  /etc/localtime
RUN mkdir /secrets
COPY templates /templates
COPY buildsites.py /buildsites.py
COPY check_cert.py /check_cert.py
COPY main.py /main.py
RUN chmod 755 /main.py
EXPOSE 5000
CMD ["python", "/main.py"]
