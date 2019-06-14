from flask_restplus import Namespace, Resource
from app.models.marshal import posts_public_fields
from app.api.auth import token_auth
from app.models.post import UserPost, GuildPost, RosterPost
from flask import g

api = Namespace('posts', description='Posts operations')


posts_public = api.model('Post', posts_public_fields)


class RestPost(Resource):
    method_decorators = token_auth.login_required


@api.route('')
class AllPosts(RestPost):
    def get(self):
        return g.current_user.posts


@api.route('/user')
class AllUserPosts(RestPost):
    def get(self):
        return g.current_user.userPosts

    def post(self):
        return


@api.route('/user/<id>')
class SpecificUserPost(RestPost):
    def get(self, id):
        return g.current_user.userPosts

    def put(self, id):
        return

    def delete(self, id):
        return


@api.route('/guild')
class AllGuildPosts(RestPost):
    def get(self):
        return g.current_user.userPosts

    def post(self):
        return


@api.route('/guild/<id>')
class SpecificGuildPost(RestPost):
    def get(self, id):
        return

    def put(self, id):
        return

    def delete(self, id):
        return


@api.route('/roster')
class AllRosterPosts(RestPost):
    def get(self):
        return g.current_user.userPosts

    def post(self):
        return


@api.route('/roster/<id>')
class SpecificRosterPost(RestPost):
    def get(self, id):
        return

    def put(self, id):
        return

    def delete(self, id):
        return
