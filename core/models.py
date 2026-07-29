from django.db import models
from django.contrib.auth.models import AbstractUser


class Company(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = (
        ("dispatcher", "Dispatcher"),
        ("driver", "Driver"),
        ("user", "User"),
        ("store","Store"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)


class Dispatcher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class UserAtLocation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.address} - {self.company}"


class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Status(models.IntegerChoices):
    NOV = 1, "Nov"
    PRIHVACEN = 2, "Prihvacen"
    PREUZETO = 3, "Roba je preuzeta"
    ZAVRSEN = 4, "Zavrsen"
    OTKAZAN = 5, "Otkazan"


class Route(models.Model):
    start_location = models.CharField(max_length=150)
    end_location = models.CharField(max_length=150)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_creates")
    taken_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="user_takes")
    date_created = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=Status.choices, default=Status.NOV)
    number_of_boxes = models.IntegerField(blank=True, null=True)
    eta = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.start_location} - {self.end_location}"


class RouteStatusHistory(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="status_history")
    status = models.IntegerField(choices=Status.choices)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
