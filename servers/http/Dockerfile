FROM alpine:3.9

# Install packages
RUN apk update && \
    apk add --no-cache \
    lighttpd \
    openssl \
    curl && \
    rm -rf /var/cache/apk/*


# Check every minute if lighttpd responds within 1 second and update
# container health status accordingly.
HEALTHCHECK --interval=1m --timeout=1s \
  CMD curl -f http://localhost/ || exit 1

# Expose http(s) ports
EXPOSE 80 443

# Make configuration path and webroot a volume
VOLUME /etc/lighttpd/
VOLUME /var/www/

ENTRYPOINT ["/usr/sbin/lighttpd", "-D", "-f", "/etc/lighttpd/lighttpd.conf"]
