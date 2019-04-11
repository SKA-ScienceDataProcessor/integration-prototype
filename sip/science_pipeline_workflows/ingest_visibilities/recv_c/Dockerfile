FROM alpine:3.8 as build
RUN apk add build-base cmake
COPY . /build_dir/
WORKDIR /build_dir/build
RUN cmake .. && make -j4

FROM alpine:3.8
RUN addgroup -S sip && adduser -S sip -G sip
# Need to figure out a way of running as non-root user with bind mounts.
#USER sip
WORKDIR /home/sip
COPY --from=build /build_dir/build/recv .
ENTRYPOINT ["./recv"]
CMD []
