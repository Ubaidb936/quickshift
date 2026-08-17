async def invalidate_search_cache(redis) -> int:
    """Delete all search-result cache entries (qs:sw:*).

    Called whenever worker data changes so businesses get fresh results
    on their next search rather than waiting for TTL expiry.

    Uses SCAN (non-blocking) instead of KEYS to avoid blocking Redis
    on large key sets. Returns the number of keys deleted.
    """
    keys = [key async for key in redis.scan_iter(match="qs:sw:*")]
    if keys:
        await redis.delete(*keys)
    return len(keys)
