FROM kalilinux/kali-rolling:latest

# Installe directement les outils sans meta-package "light"
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      nmap \
      whois \
      sqlmap \
      metasploit-framework \
      nikto \
      gobuster \
      wfuzz \
      jq \
      curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/toolbox

