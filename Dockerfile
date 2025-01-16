FROM registry.access.redhat.com/ubi9-minimal

WORKDIR /opt/podmanwatch

VOLUME ["/run/podman/podman.sock"]

RUN microdnf -y install python3.12 python3.12-pip findutils procps-ng; microdnf clean all

LABEL name="podmanwatch"
LABEL description="Publish basic status for Podman containers over HTTP"

COPY requirements.txt /tmp/requirements.txt
ENV PIP_ROOT_USER_ACTION=ignore
ENV PYTHONUNBUFFERED=1
RUN pip3.12 install --no-cache-dir --upgrade -r /tmp/requirements.txt

ADD ./src /opt/podmanwatch

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--ssl-ciphers", "TLSv1.3", "main:app"]
