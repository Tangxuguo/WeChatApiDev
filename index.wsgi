import sae
from weichat import wsgi

application = sae.create_wsgi_app(wsgi.application)