#include <stdlib.h>
#include <time.h>
#include <sys/time.h>
#include "timer.h"

struct Timer
{
    double start, elapsed;
    int paused;
};

void tmr_clear(struct Timer* self)
{
    self->paused = 1;
    self->start = self->elapsed = 0.0;
}

struct Timer* tmr_create(void)
{
    struct Timer* cls = (struct Timer*) calloc(1, sizeof(struct Timer));
    tmr_clear(cls);
    return cls;
}

double tmr_elapsed(struct Timer* self)
{
    if (self->paused) return self->elapsed;
    const double now = tmr_get_timestamp();
    self->elapsed += (now - self->start);
    self->start = now;
    return self->elapsed;
}

void tmr_free(struct Timer* self)
{
    free(self);
}

double tmr_get_timestamp(void)
{
#if _POSIX_MONOTONIC_CLOCK > 0
    /* Use monotonic clock if available. */
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
#else
    /* Use gettimeofday() as fallback. */
    struct timeval tv;
    gettimeofday(&tv, 0);
    return tv.tv_sec + tv.tv_usec / 1e6;
#endif
}

void tmr_pause(struct Timer* self)
{
    if (self->paused) return;
    (void)tmr_elapsed(self);
    self->paused = 1;
}

static void tmr_restart(struct Timer* self)
{
    self->paused = 0;
    self->start = tmr_get_timestamp();
}

void tmr_resume(struct Timer* self)
{
    if (!self->paused) return;
    tmr_restart(self);
}

void tmr_start(struct Timer* self)
{
    self->elapsed = 0.0;
    tmr_restart(self);
}
