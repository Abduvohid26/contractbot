from environs import Env
env = Env()
env.read_env()
BOT_TOKEN=env.str('BOT_TOKEN')
ADMINS=env.list('ADMINS')
CHANNEL=env.list('CHANNEL')
CHECK_ADMIN=env.str('CHECK_ADMIN')