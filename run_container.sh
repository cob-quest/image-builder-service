docker build -t image-builder:1.0 .
docker run -v /var/run/docker.sock:/var/run/docker.sock -it -p 5000:5000 --privileged --name image-builder image-builder:1.0