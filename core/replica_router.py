import logging

from django.conf import settings

logger = logging.getLogger(getattr(settings, "COMMON_LOGGER", "django"))


class ReplicationRouter:
    def db_for_read(self, model, **hints):
        """
        Randomly pick a database to read from

        Note: If you have more than one replica, your db_for_read() method should instead randomly choose a replica, as the example in the Django docs does: return random.choice(['replica1', 'replica2']).
        """
        # return random.choice([key for key in settings.DATABASES]) # for All database
        # return random.choice(['replica1', 'replica2']) # for replica database
        return "replica1"

    def db_for_write(self, model, **hints):
        """
        Always send write queries to the master database.
        """
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """
        This isn't really applicable for this use-case.
        """
        return True

        """
        Relations between objects are allowed if both objects are
        in the primary/replica pool.

        db_set = {'default', 'replica'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None
        """

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Only allow migration operations on the master database, just in case.
        """
        if db == "default":
            return True
        return None
