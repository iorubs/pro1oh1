from rest_framework_nested import routers
from django.conf.urls import url, include
from django.contrib import admin

from authentication.views import AccountViewSet, LoginView, LogoutView
from quickrun.views import singleRunView, staticAnalView
from projects.views import ProjectViewSet, FileViewSet, projectStaticView, projectRunView, cloneGitProjectView, pushGitProjectView
from tutorials.views import TutorialGroupViewSet, TutorialViewSet
from pro1oh1.views import IndexView, userCountView

router = routers.SimpleRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'files', FileViewSet)
router.register(r'tutorials', TutorialViewSet)
router.register(r'tutorial_groups', TutorialGroupViewSet)

accounts_router = routers.NestedSimpleRouter(
    router, r'accounts', lookup='account'
)
accounts_router.register(r'projects', ProjectViewSet)

projects_router = routers.NestedSimpleRouter(
    router, r'projects', lookup='project'
)
projects_router.register(r'files', FileViewSet)

tutorial_groups_router = routers.NestedSimpleRouter(
    router, r'tutorial_groups', lookup='tutorialgroup'
)
tutorial_groups_router.register(r'tutorials', TutorialViewSet)

urlpatterns = [
        url(r'^api/v1/', include(router.urls)),

        url(r'^api/v1/', include(accounts_router.urls)),

        url(r'^api/v1/', include(projects_router.urls)),

        url(r'^api/v1/', include(tutorial_groups_router.urls)),

        url(r'^api/v1/user-count/$', userCountView),

        url(r'^api/v1/auth/login/$', LoginView.as_view(), name='login'),

        url(r'^api/v1/auth/logout/$', LogoutView.as_view(), name='logout'),

        url(r'^api/v1/quick-run/singlerun/$', singleRunView),

        url(r'^api/v1/quick-run/staticrun/$', staticAnalView),

        url(r'^api/v1/project/staticrun/$', projectStaticView),

        url(r'^api/v1/project/run/$', projectRunView),

        url(r'^api/v1/project/git-clone/$', cloneGitProjectView),

        url(r'^api/v1/project/git-push/$', pushGitProjectView),

        url('^.*$', IndexView.as_view(), name='index'),
]
