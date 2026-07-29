from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse

from django.utils import timezone
from django.template.loader import render_to_string
from datetime import datetime, timedelta

from core.models import Route, Status, RouteStatusHistory

from xhtml2pdf import pisa
from io import BytesIO

class RoutesPDFAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_this_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_last_month = (start_this_month - timedelta(days=1)).replace(day=1)
        end_last_month = start_this_month - timedelta(microseconds=1)

        routes = Route.objects.filter(
            date_created__gte=start_last_month,
            date_created__lte=end_last_month
        ).order_by("date_created")

        subject = f"<h2>{request.user.first_name} {request.user.last_name} {start_last_month.strftime('%d.%m.%Y')} - {end_last_month.strftime('%d.%m.%Y')} </h2>"

        rows = []
        index = 0
        for route in routes:
            if route.status != Status.ZAVRSEN:
                continue
            index += 1
            end_time = RouteStatusHistory.objects.filter(
                route = route,
                status=Status.ZAVRSEN
            ).first().changed_at.strftime("%H:%M")
            row = f"""
              <tr> 
                <td>{index}</td>
                <td>{route.date_created.strftime('%d.%m.%Y')}</td>
                <td>{route.date_created.strftime("%H:%M")}</td>
                <td>{end_time}</td>
                <td>{route.start_location}</td>
                <td>{route.end_location}</td>
                <td>{route.taken_by}</td>
                <td>    </td>
              </tr>
            """
            rows.append(row)
        html_rows = "".join(rows)

        TEMPLATE.format(
            subject,
            html_rows,
        )

        output_filename = "test.pdf"

        buffer = BytesIO()

        html = TEMPLATE.format(subject, html_rows)
        pisa_status = pisa.CreatePDF(
            html,
            dest=buffer
        )

        if pisa_status.err:
            return HttpResponse("Error generating PDF", status=500)

        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="routes.pdf"'

        return response


TEMPLATE = """
<head>
<style>
table {{
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}}

td, th {{
  border: 1px solid #dddddd;
  text-align: left;
  padding: 8px;
}}

tr:nth-child(even) {{
  background-color: #dddddd;
}}
</style>
</head>
<body>
{}
<table>
  <tr>
    <th>Redni broj</th>
    <th>Datum</th>
    <th>Vreme poziva</th>
    <th>Vreme zavrsetka</th>
    <th>Polazna stanica</th>
    <th>Zavrsna stanica</th>
    <th>Vozac</th>
    <th>Cena</th>
  </tr>
  {}
</table>
</body>
"""