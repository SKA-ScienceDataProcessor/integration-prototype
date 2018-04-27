FROM fluent/fluentd:v0.12-onbuild

# below RUN includes plugin as examples elasticsearch is not required
# you may customize including plugins as you wish

ADD https://github.com/stackhpc/fluentd-monasca/archive/master.tar.gz /fluentd-monasca.tar.gz
RUN mkdir /fluentd-monasca \
    && cd /fluentd-monasca \
    && tar -zxf /fluentd-monasca.tar.gz \
    && rm /fluentd-monasca.tar.gz

RUN apk add --update --virtual .build-deps sudo build-base ruby-dev ruby-libs \
        && gem install fluent-plugin-secure-forward \
        && gem sources --clear-all \
        && cd /fluentd-monasca/fluentd-monasca-master \
        && gem build fluentd-monasca-output.gemspec \
        && gem install fluentd-monasca-output-0.0.1.gem \
        && fluent-gem install fluentd-monasca-output-0.0.1.gem \
        && rm -rf /fluentd-monasca \
        && apk del .build-deps \
        && rm -rf /var/cache/apk/* /home/fluent/.gem/ruby/2.3.0/cache/*.gem

EXPOSE 24284
