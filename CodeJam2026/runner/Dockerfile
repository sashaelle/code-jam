FROM python:3.12-slim

WORKDIR /app

# Install Node.js runtime, Java compiler/runtime, and Linux C++ tooling.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl gnupg ca-certificates g++ make default-jdk-headless \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs \
    && g++ --version \
    && javac --version \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

ENV PYTHONUNBUFFERED=1
EXPOSE 5000

CMD ["python", "hello.py"]
