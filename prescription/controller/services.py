# TODO import this from a json dockerized
services = {
    'host': 'https://mock-api-challenge.dev.iclinic.com.br',
    'physicians': {
        'method': 'GET',
        'path': '/physicians/',
        'token': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJzZXJ2aWNlIjoicGh5c2ljaWFucyJ9.Ei58MtFFGBK4uzpxwnzLxG0Ljdd-NQKVcOXIS4UYJtA',
        'timeout': 4,
        'retry': 2,
        'cache-ttl': 48
    },
    'clinics': {'method': 'GET',
                'path': '/clinics/',
                'token': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJzZXJ2aWNlIjoiY2xpbmljcyJ9.r3w8KS4LfkKqZhOUK8YnIdLhVGJEqnReSClLCMBIJRQ',
                'timeout': 5,
                'retry': 3,
                'cache-ttl': 72
                },
    'patients': {'method': 'GET',
                 'path': '/patients/',
                 'token': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJzZXJ2aWNlIjoicGF0aWVudHMifQ.Pr6Z58GzNRtjX8Y09hEBzl7dluxsGiaxGlfzdaphzVU',
                 'timeout': 3,
                 'retry': 2,
                 'cache-ttl': 12
                 },
    'metrics': {
        'method': 'POST',
        'path': '/metrics',
        'token': '',
        'timeout': 6,
        'retry': 5,
        'cache-ttl': 0
    }
}
