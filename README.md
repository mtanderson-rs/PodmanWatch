Podman local containers - monitor running / not-running status. Runs in a container. Easy to probe from a monitoring tool with http. Runs on port 8000 by default.

The package podman-docker (or other package for podman docker.sock emulation) should be installed on the podman host.

- /api/podman-list
- /api/podman-status
- /api/podman-status/{cname}

---

Build image

```podman build -t podmanwatch .```

Run image

```podman run -d --privileged -p 8000:8000 --name podmanwatch -v /run/podman/podman.sock:/var/run/docker.sock:Z podmanwatch```
