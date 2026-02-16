FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    nodejs \
    npm \
    git \
    curl \
    wget \
    vim \
    build-essential \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -s /bin/bash openclaw
USER openclaw

# Set working directory
WORKDIR /home/openclaw/workspace

# Install Python packages
RUN pip3 install --user \
    jupyter \
    numpy \
    pandas \
    matplotlib \
    scikit-learn \
    requests \
    flask

# Install Node global packages
RUN npm install -g typescript ts-node

# Clone and setup openclaw
RUN git clone https://github.com/yourusername/openclaw.git /home/openclaw/openclaw || true

# Setup environment
ENV PATH=/home/openclaw/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Expose ports
EXPOSE 8080 8888 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command
CMD ["/bin/bash"]
