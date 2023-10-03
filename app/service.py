from torpedo import Host, CONFIG
from redis_wrapper import RegisterRedis


from app.listeners import listeners
from app.routes import blueprint_group

if __name__ == "__main__":

    # Setup redis wrapper
    RegisterRedis.register_redis_cache(CONFIG.config["REDIS_CACHE_HOSTS"])

    # Register listeners
    Host._listeners = listeners

    # Register DB
    Host._db_config = CONFIG.config["DB_CONNECTIONS"]

    # register combined blueprint group here.
    # these blueprints are defined in the routes directory and has to be
    # collected in init file otherwise route will end up with 404 error.
    Host._blueprint_group = blueprint_group
    Host.run()
