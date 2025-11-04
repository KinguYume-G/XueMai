"""
速率限制配置
"""
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AnonymousRateThrottle(AnonRateThrottle):
    rate = '30/min'


class AuthenticatedRateThrottle(UserRateThrottle):
    rate = '60/min'

