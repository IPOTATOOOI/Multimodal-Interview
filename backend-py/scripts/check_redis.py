import json
import sys

# 尝试从项目配置读取 REDIS_URL，否则使用默认
try:
    from app.core.config import settings
    redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
except Exception:
    redis_url = 'redis://localhost:6379/0'

print(f"Using Redis URL: {redis_url}")

try:
    import redis
except Exception as e:
    print('redis module not available:', e)
    sys.exit(2)

try:
    r = redis.from_url(redis_url, decode_responses=True)
    keys = r.keys('swcup:*')
    print('Found', len(keys), 'keys matching swcup:*')
    for k in keys:
        v = r.get(k)
        # try parse JSON
        try:
            parsed = json.loads(v)
            pretty = json.dumps(parsed, ensure_ascii=False)
            print('---', k)
            print(pretty[:2000])
        except Exception:
            print('---', k)
            if v is None:
                print('<nil>')
            else:
                print(v[:2000])
except Exception as e:
    print('Failed to query Redis:', e)
    sys.exit(2)

print('Done')
