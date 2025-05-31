FROM kalilinux/kali-rolling:latest

# Installe directement les outils sans meta-package "light"
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      nmap \
      whois \
      subfinder \
      dnsenum \
      sqlmap \
      metasploit-framework \
      nikto \
      gobuster \
      wfuzz \
      jq \
      curl \
      whatweb \
      wpscan \
      hydra \
      gvm-tools \
      openvas-scanner && \
    # Installation de testssl.sh depuis GitHub
    git clone https://github.com/drwetter/testssl.sh.git /opt/testssl.sh && \
    ln -s /opt/testssl.sh/testssl.sh /usr/local/bin/testssl.sh && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/toolbox

