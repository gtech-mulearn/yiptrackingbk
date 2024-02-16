import datetime, pytz
from datetime import timedelta
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import csv, gzip, openpyxl, io

class CommonUtils:
    @staticmethod
    def get_paginated_queryset(
        queryset: QuerySet,
        request,
        search_fields,
        sort_fields: dict = None,
        is_pagination: bool = True,
    ) -> QuerySet:
        if sort_fields is None:
            sort_fields = {}

        page = int(request.query_params.get("pageIndex", 1))
        per_page = int(request.query_params.get("perPage", 10))
        search_query = request.query_params.get("search")
        sort_by = request.query_params.get("sort")
        if search_query:
            query = Q()
            for field in search_fields:
                query |= Q(**{f"{field}__icontains": search_query})

            queryset = queryset.filter(query)

        if sort_by:
            sort = sort_by[1:] if sort_by.startswith("-") else sort_by
            if sort_field_name := sort_fields.get(sort):
                if sort_by.startswith("-"):
                    sort_field_name = f"-{sort_field_name}"

                queryset = queryset.order_by(sort_field_name)
        if is_pagination:
            paginator = Paginator(queryset, per_page)
            try:
                queryset = paginator.page(page)
            except PageNotAnInteger:
                queryset = paginator.page(1)
            except EmptyPage:
                queryset = paginator.page(paginator.num_pages)

            return {
                "queryset": queryset,
                "pagination": {
                    "count": paginator.count,
                    "totalPages": paginator.num_pages,
                    "isNext": queryset.has_next(),
                    "isPrev": queryset.has_previous(),
                    "nextPage": queryset.next_page_number()
                    if queryset.has_next()
                    else None,
                },
            }

        return queryset

    @staticmethod
    def generate_csv(queryset: QuerySet, csv_name: str) -> HttpResponse:
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{csv_name}.csv"'
        fieldnames = list(queryset[0].keys())
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(queryset)

        compressed_response = HttpResponse(
            gzip.compress(response.content),
            content_type="text/csv",
        )
        compressed_response[
            "Content-Disposition"
        ] = f'attachment; filename="{csv_name}.csv"'
        compressed_response["Content-Encoding"] = "gzip"

        return compressed_response


class DateTimeUtils:
    """
    A utility class for handling date and time operations.

    """

    @staticmethod
    def get_current_utc_time() -> datetime.datetime:
        """
        Returns the current time in UTC.

        Returns:
            datetime.datetime: The current time in UTC.
        """
        local_now = datetime.datetime.now(pytz.timezone("UTC"))
        return DateTimeUtils.format_time(local_now)

    @staticmethod
    def format_time(date_time: datetime.datetime) -> datetime.datetime:
        """
        Formats a datetime object to the format '%Y-%m-%d %H:%M:%S'.

        Args:
            date_time (datetime.datetime): The datetime object to format.

        Returns:
            datetime.datetime: The formatted datetime object.
        """

        return date_time.replace(microsecond=0)

    @staticmethod
    def get_start_and_end_of_previous_month():
        today = DateTimeUtils.get_current_utc_time()
        start_date = today.replace(day=1)
        end_date = start_date.replace(
            day=1, month=start_date.month % 12 + 1
        ) - timedelta(days=1)
        return start_date, end_date


class CSVUtils:
    def read_excel_file(self, file_obj):
        workbook = openpyxl.load_workbook(filename=io.BytesIO(file_obj.read()))
        sheet = workbook.active

        rows = []
        for row in sheet.iter_rows(values_only=True):
            if all(value is None for value in row):break
            row_dict = {
                header.value: cell_value for header, cell_value in zip(sheet[1], row)
            }
            rows.append(row_dict)
        workbook.close()

        return rows
    @staticmethod
    def generate_csv(queryset: QuerySet, csv_name: str) -> HttpResponse:
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{csv_name}.csv"'
        fieldnames = list(queryset[0].keys())
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(queryset)

        compressed_response = HttpResponse(
            gzip.compress(response.content),
            content_type="text/csv",
        )
        compressed_response[
            "Content-Disposition"
        ] = f'attachment; filename="{csv_name}.csv"'
        compressed_response["Content-Encoding"] = "gzip"

        return compressed_response