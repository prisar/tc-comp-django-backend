"""mechanics_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from app.controllers.user import UserDetailAPI, UserRoleAPI, UserListAPI
from app.controllers.workspace import WorkspaceListAPI, WorkspaceDetailAPI, WorkspaceCopyAPI
from app.controllers.rule import RuleListAPI, RuleDetailAPI, RuleCopyAPI
from app.controllers.rule_version import RuleVersionListAPI, RuleVersionDetailAPI, RuleVersionModifyAPI
from app.controllers.project import ProjectDetailAPI, ProjectListAPI
from app.controllers.rule_function import RuleFunctionAPI


urlpatterns = [
    path('api/v1/users', UserListAPI.as_view()),
    path('api/v1/users/<id>', UserDetailAPI.as_view()),
    path('api/v1/users/<id>/role', UserRoleAPI.as_view()),
    path('api/v1/workspaces', WorkspaceListAPI.as_view()),
    path('api/v1/workspaces/<id>', WorkspaceDetailAPI.as_view()),
    path('api/v1/workspaces/<id>/copy', WorkspaceCopyAPI.as_view()),
    path('api/v1/rules', RuleListAPI.as_view()),
    path('api/v1/rules/<id>', RuleDetailAPI.as_view()),
    path('api/v1/rules/<id>/copy', RuleCopyAPI.as_view()),
    path('api/v1/rules/<id>/rule-versions', RuleVersionListAPI.as_view()),
    path('api/v1/rule-versions/<id>', RuleVersionDetailAPI.as_view()),
    path('api/v1/rule-versions/<id>/<modify_type>', RuleVersionModifyAPI.as_view()),
    path('api/v1/projects', ProjectListAPI.as_view()),
    path('api/v1/projects/<id>', ProjectDetailAPI.as_view()),
    path('api/v1/rules/functions/<function>', RuleFunctionAPI.as_view()),
]

format_suffix_patterns(urlpatterns)