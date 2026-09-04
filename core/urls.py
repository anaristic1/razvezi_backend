from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path("routes/", views.RouteList.as_view()),
    path("routes/<int:id>/", views.RouteDetail.as_view()),
    path("routes/<int:route_id>/take_product/", views.DriverTakesProductView.as_view()),
    path("routes/<int:route_id>/finish/", views.DriverFinishesRouteView.as_view()),
    path("routes/<int:route_id>/cancel/", views.DispatcherClosesRoute.as_view()),
    path("driver_routes/", views.DriverRoutes.as_view()),
    path("drivers_routes_today/", views.DriverRoutesToday.as_view()),
    path("created_routes/", views.UserCreatedRoutes.as_view()),
    path("create_new_route/", views.create_route),
    path("routes/<int:route_id>/history/", views.route_history),
    path("login/", views.LoginView.as_view(), name='login'),
    path("logout/", views.LogoutView.as_view(), name='logout'),
]

urlpatterns = format_suffix_patterns(urlpatterns)