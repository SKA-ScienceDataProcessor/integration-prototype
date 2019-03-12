#ifndef RECV_THREAD_BARRIER_H_
#define RECV_THREAD_BARRIER_H_

#ifdef __cplusplus
extern "C" {
#endif

struct ThreadBarrier;

/**
 * @brief Creates a new thread barrier.
 */
struct ThreadBarrier* barrier_create(int num_threads);

/**
 * @brief Destroys the thread barrier.
 */
void barrier_free(struct ThreadBarrier* self);

/**
 * @brief Causes threads to wait at the barrier.
 */
int barrier_wait(struct ThreadBarrier* self);

#ifdef __cplusplus
}
#endif

#endif /* include guard */
