FROM python:3

COPY . /src
RUN pip3 install --no-cache-dir -r /src/requirements.pip

RUN python3 -m pip install --upgrade /src && \
	cp /usr/local/bin/flumewater_exporter /flumewater_exporter

EXPOSE 9183 

ENTRYPOINT ["/flumewater_exporter"]
