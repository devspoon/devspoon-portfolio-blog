#! /bin/bash

chmod 755 /www/devspoon-portfolio-blog/celery_etc/init.d/celeryd
chmod 755 /www/devspoon-portfolio-blog/celery_etc/init.d/celerybeat
chown root:root /www/devspoon-portfolio-blog/celery_etc/init.d/celeryd
chown root:root /www/devspoon-portfolio-blog/celery_etc/init.d/celerybeat
cp /www/devspoon-portfolio-blog/celery_etc/init.d/celeryd /etc/init.d/celeryd
cp /www/devspoon-portfolio-blog/celery_etc/init.d/celerybeat /etc/init.d/celerybeat
cp /www/devspoon-portfolio-blog/celery_etc/default/celeryd /etc/default/celeryd

/etc/init.d/celeryd start
/etc/init.d/celerybeat start