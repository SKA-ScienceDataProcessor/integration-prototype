FROM gcc:8.2 as build
COPY recv.c /build_recv/
WORKDIR /build_recv
RUN gcc -O3 -Wall -Wextra -pthread -o recv recv.c

FROM alpine:3.8
RUN apk --no-cache add ca-certificates libc6-compat
RUN addgroup -S sip && adduser -S sip -G sip
# Need to figure out a way of running as non-root user with bind mounts.
#USER sip
WORKDIR /home/sip
COPY --from=build /build_recv/recv .
ENTRYPOINT ["./recv"]
CMD []
