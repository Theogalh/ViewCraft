from viewcraft import create_app, db
from viewcraft.models import User, Post, Character, Roster, Guild

application = create_app()


@application.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Character': Character, 'Roster': Roster, 'Guild': Guild}


if __name__ == "__main__":
    application.run()
