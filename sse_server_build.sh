docker stop kipris-sse
docker rm kipris-sse
docker build -t mcp-kipris-sse -f ./Dockerfile.sse .
docker run -d --name kipris-sse -p 6274:6274 mcp-kipris-sse
