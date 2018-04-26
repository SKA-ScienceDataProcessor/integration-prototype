FROM fluent/fluentd:v0.12-onbuild

# below RUN includes plugin as examples elasticsearch is not required
# you may customize including plugins as you wish

RUN apk add --update --virtual .build-deps \
        sudo build-base ruby-dev ruby-libs \
        && sudo gem install fluent-plugin-secure-forward \
        && sudo gem sources --clear-all \
        && apk del .build-deps \
        && rm -rf /var/cache/apk/* /home/fluent/.gem/ruby/2.3.0/cache/*.gem

EXPOSE 24284

ADD https://github.com/stackhpc/fluentd-monasca/archive/master.tar.gz /fluentd-monasca.tar.gz
RUN mkdir /fluentd-monasca \
    && cd /fluentd-monasca \
    && tar -zxf /fluentd-monasca.tar.gz \
    && rm /fluentd-monasca.tar.gz
RUN cd /fluentd-monasca/fluentd-monasca-master \
    && gem build fluentd-monasca-output.gemspec \
    && gem install fluentd-monasca-output-0.0.1.gem \
    && fluent-gem install fluentd-monasca-output-0.0.1.gem \
    && rm -rf /fluentd-monasca
