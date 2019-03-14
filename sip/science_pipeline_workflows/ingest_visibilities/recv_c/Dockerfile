FROM alpine:3.8 as build
RUN apk add build-base
WORKDIR /build_dir
COPY recv.c .
COPY VERSION .
RUN RECV_VERSION="\"$(cat VERSION)\"" && \
    gcc -O3 -Wall -Wextra -pthread -o recv -DRECV_VERSION=$RECV_VERSION recv.c

FROM alpine:3.8
RUN addgroup -S sip && adduser -S sip -G sip
# Need to figure out a way of running as non-root user with bind mounts.
#USER sip
WORKDIR /home/sip
COPY --from=build /build_dir/recv .
ENTRYPOINT ["./recv"]
CMD []
