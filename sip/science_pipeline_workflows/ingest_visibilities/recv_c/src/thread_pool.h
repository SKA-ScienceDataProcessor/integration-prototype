#ifndef RECV_THREAD_POOL_H_
#define RECV_THREAD_POOL_H_

#ifdef __cplusplus
extern "C" {
#endif

struct ThreadPool;

/**
 * @brief Creates a new thread pool.
 */
struct ThreadPool* threadpool_create(int num_threads);

/**
 * @brief Enqueues a task for the thread pool to execute.
 */
void threadpool_enqueue(struct ThreadPool* self,
        void *(*thread_func)(void*), void *arg);

/**
 * @brief Destroys the thread pool.
 */
void threadpool_free(struct ThreadPool* self);

#ifdef __cplusplus
}
#endif

#endif /* include guard */
