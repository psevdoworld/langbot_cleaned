from rest_framework import permissions
BOTAUTHTOKEN = "example_token" # TODO:  Ну как то по другому это должно быть


class OnlyBot(permissions.BasePermission):

    def has_permission(self, request, view):

        if request.headers.get("BotAuthToken") == BOTAUTHTOKEN:
            return True
        return False
