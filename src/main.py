from datetime import datetime
from typing import List, Dict
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from podman import PodmanClient

"""
This should be set up only for very basic and *non-sensitive* read operations
such as status checks.

The docker.sock connection has full privileges.
"""

socket_uri = "unix:////var/run/docker.sock"

log_format = ("%(asctime)s %(levelname)s %(name)s %(funcName)s "
              "%(lineno) -5d: %(message)s")
logging.basicConfig(level="WARNING",
                    format=log_format,
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger("podmanwatch").setLevel("WARNING")

app = FastAPI()

class PodmanContainerSummary(BaseModel):
    ContainerID: str
    Image: str
    Command: List[str]
    LocalVolumes: int
    Size: int
    RWSize: int
    Created: datetime
    Status: str
    Names: str

@app.get("/api/podman-list", response_model=List[PodmanContainerSummary])
def list_containers():
    # avoid any full .inspect() since it may include sensitive data
    with PodmanClient(base_url=socket_uri) as client:
        if not client.ping():
            # verify that the container volume to podman.sock is mounted with :z
            # podmanwatch container is running privileged
            # podman-docker package is installed for docker.sock compatibility
            logger.error(f"{socket_uri} connection error.")
            raise HTTPException(status_code=500, detail="podman.sock connection error")
        return client.df()["Containers"]

@app.get("/api/podman-status", response_model=Dict[str, str])
def container_status():
    status_collection = {}
    with PodmanClient(base_url=socket_uri) as client:
        if not client.ping():
            logger.error(f"{socket_uri} connection error.")
            raise HTTPException(status_code=500, detail="podman.sock connection error")
        for container in client.containers.list():
            try:
                container.reload()
            except Exception:
                raise HTTPException(status_code=500, detail=f"Unknown error on container reload")
            status_collection[container.name] = container.status
        return status_collection

@app.get("/api/podman-status/{cname}", response_model=str)
def container_status(cname: str):
    with PodmanClient(base_url=socket_uri) as client:
        if not client.ping():
            logger.error(f"{socket_uri} connection error.")
            raise HTTPException(status_code=500, detail="podman.sock connection error")
        quickstatus = filter(lambda x: x["Names"] == cname, client.df()["Containers"])
        try:
            return str(next(quickstatus)["Status"])
        except StopIteration:
            raise HTTPException(status_code=404, detail=f"No status for container {cname}")
        except Exception:
            raise HTTPException(status_code=500, detail=f"Unknown error retrieving status")
