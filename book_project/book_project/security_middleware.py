import logging
from django.http import HttpResponseForbidden
from django.conf import settings

logger = logging.getLogger('django.security')


class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Блокируем подозрительные User-Agent
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        suspicious_agents = ['sqlmap', 'nikto', 'metasploit', 'nmap']

        if any(agent in user_agent for agent in suspicious_agents):
            logger.warning(f'Blocked suspicious user agent: {user_agent}')
            return HttpResponseForbidden('Access denied')

        # Логируем попытки доступа к чувствительным URLs
        if any(path in request.path for path in ['/admin', '/php', '/wp-admin']):
            logger.info(f'Access attempt to sensitive path: {request.path}')

        response = self.get_response(request)
        return response