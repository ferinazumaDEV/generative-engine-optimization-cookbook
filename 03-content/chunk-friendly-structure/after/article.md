# Caching Strategies for Web APIs

Caching is one of the highest-leverage ways to make a web API faster and cheaper to run. This guide explains the main strategies, when each one applies, and the trade-offs you accept when you choose it.

## Why cache at all

Every request that hits your database or an upstream service costs time and money. A cache stores the result of expensive work so that later requests can be served from fast memory instead of repeating that work. The goal is to serve the same answer with less latency and less load.

Caching pays off most when reads greatly outnumber writes and when the same data is requested many times. If every request is unique, a cache adds complexity without helping.

## Where a cache can live

There are three common places to put a cache:

- **Client-side:** the browser or mobile app stores responses locally, so repeated views cost no network at all.
- **Edge / CDN:** a content delivery network caches responses close to the user, cutting round-trip time for everyone in a region.
- **Server-side:** an in-memory store such as Redis or Memcached sits between your application and its database.

Most production systems combine all three layers rather than relying on a single one.

## Time-based expiration

The simplest strategy is a time-to-live, or TTL. You store a value and mark it to expire after a fixed number of seconds. Until it expires, every request is served from the cache; after it expires, the next request recomputes the value and stores it again.

TTLs are easy to reason about and require no coordination. The cost is staleness: for up to the length of the TTL, clients may see data that is out of date.

## Cache invalidation

The hardest problem in caching is knowing when a cached value is no longer correct. There are two broad approaches:

- **Write-through:** every time you update the underlying data, you also update or delete the cached copy in the same operation.
- **Event-based:** a change somewhere in the system emits an event, and a listener clears the affected cache keys.

Write-through keeps the cache and the source of truth consistent at the cost of slower writes. Event-based invalidation decouples the two but introduces a window where the cache can be wrong.

## Cache keys

A cache key uniquely identifies the thing you are storing. A good key includes every input that changes the output, such as the resource id, the requesting user's permissions, and the API version.

If you leave an input out of the key, you will serve one user's data to another. If you put too much in the key, your hit rate collapses because almost every request looks unique.

## Stampedes and cold caches

When a popular cached value expires, many requests can miss the cache at the same instant and all recompute it together. This is called a cache stampede, and it can overwhelm the very database the cache was meant to protect.

Two defenses are common:

- **Locking:** the first request to miss takes a lock and recomputes while the others wait for the fresh value.
- **Early recomputation:** you refresh the value slightly before it expires, so the cache is never actually empty during traffic.

## What to measure

You cannot tune a cache you are not measuring. Track the hit rate, the latency of hits versus misses, and the staleness your users actually experience. A cache with a low hit rate is often worse than no cache, because you pay the lookup cost and still fall through to the database.

Start simple with a TTL, measure, and add invalidation and stampede protection only where the numbers show you need them.
