import json
from django.views.generic import TemplateView
from django.http import Http404, HttpResponse
from io import StringIO
from base import mods
from django.contrib.auth.models import User
import csv
import pandas as pd
from io import BytesIO


def dict_to_csv(values, name):
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow([name])
    for value in values.items():
        writer.writerow(value)
    return csv_buffer.getvalue()


def build_census_map(census):
    rows = {"Name": [], "Id": []}
    print("aaaaaaaaaa")
    for user in census:
        print(user)
        rows.get("Name").append(User.objects.get(pk=int(user)).username)
        rows.get("Id").append(user)
    return rows


def export_census_xls(request, **kwargs):
    vid = kwargs.get("voting_id", 0)
    r = mods.get("voting", params={"id": vid})
    a = json.loads(json.dumps(r[0]))
    c = mods.get("census", params={"voting_id": vid})
    file_name = "censo-" + a.get("name") + "-" + str(a.get("end_date"))
    data = build_census_map(c.get("voters"))

    df = pd.DataFrame(data)

    response = HttpResponse(content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = f'attachment; filename="{file_name}.xls"'

    # Write the DataFrame to the HttpResponse as an Excel file
    df.to_excel(response, index=False)

    return response


def download_census_csv(request, **kwargs):
    vid = kwargs.get("voting_id", 0)
    r = mods.get("voting", params={"id": vid})
    a = json.loads(json.dumps(r[0]))
    c = mods.get("census", params={"voting_id": vid})
    file_name = "censo-" + a.get("name") + "-" + str(a.get("end_date"))
    rows = build_census_map(c.get("voters"))
    csv_data = dict_to_csv(rows, a.get("name"))
    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{file_name}.csv"'
    return response


def export_votes_xls(request, **kwargs):
    vid = kwargs.get("voting_id", 0)
    r = mods.get("voting", params={"id": vid})
    a = json.loads(json.dumps(r[0]))
    file_name = "votos-" + a.get("name") + "-" + str(a.get("end_date"))
    data = {}
    if len(a.get("postproc")) == 0:
        data = build_vote_map(a)
    else:
        type_postproc = a.get("postproc").get("type_postproc")
        if type_postproc == "DRO":
            data = process_post_voting_data(a, "droop")
        elif type_postproc == "PAR":
            data = process_post_voting_data(a, "saintLague")
        elif type_postproc == "DHO":
            data = process_dho_voting_data(a)

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for page, question in data.items():
            df = pd.DataFrame(question)
            df.to_excel(writer, sheet_name=page, index=False)

    output.seek(0)

    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{file_name}.xls"'

    return response


def download_votes_csv(request, **kwargs):
    vid = kwargs.get("voting_id", 0)
    r = 0
    a = 0
    r = mods.get("voting", params={"id": vid})
    a = json.loads(json.dumps(r[0]))
    file_name = "votos-" + a.get("name") + "-" + str(a.get("end_date"))
    data = {}
    if len(a.get("postproc")) == 0:
        data = build_vote_map(a)
    else:
        type_postproc = a.get("postproc").get("type_postproc")
        if type_postproc == "DRO":
            data = process_post_voting_data(a, "droop")
        elif type_postproc == "PAR":
            data = process_post_voting_data(a, "saintLague")
        elif type_postproc == "DHO":
            data = process_dho_voting_data(a)

    csv_data = dict_to_csv(data, a.get("name"))
    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{file_name}.csv"'
    return response


def build_vote_map(a):
    res = {}
    i = 1
    for question in a.get("questions"):
        rows = {"number": [], "option": [], "votes": []}
        k = 0
        for option in question.get("options"):
            rows["number"].append(option.get("number"))
            rows["option"].append(option.get("option"))
            if a.get("tally")[k] == option.get("number"):
                rows["votes"].append(1)
            else:
                rows["votes"].append(0)
        k = k + 1
        res["question " + str(i)] = rows
        i = i + 1
    return res


def process_dho_voting_data(a):
    res = {}
    i = 1
    j = 0
    for question in a.get("questions"):
        rows = {"number": [], "option": [], "votes": []}
        seats = []
        for seat in a.get("postproc").get("results")[j].get("dhont"):
            rows["seat " + str(seat.get("seat"))] = []
            seats.append("seat " + str(seat.get("seat")))
        for option in question.get("options"):
            rows["number"].append(option.get("number"))
            rows["option"].append(option.get("option"))
            rows["votes"].append(a.get("postproc").get("results")[j].get("votes"))
            k = 0
            for seat in seats:
                percent = (
                    a.get("postproc")
                    .get("results")[j]
                    .get("dhont")[k]
                    .get("percentaje")
                )
                rows[seat].append(percent)
                k = k + 1
            j = j + 1
        res["question " + str(i)] = rows
        i = i + 1
    return res


def process_post_voting_data(a, type):
    res = {}
    i = 1
    j = 0
    for question in a.get("questions"):
        rows = {"number": [], "option": [], "votes": [], type: []}
        for option in question.get("options"):
            rows["number"].append(option.get("number"))
            rows["option"].append(option.get("option"))
            rows["votes"].append(a.get("postproc").get("results")[j].get("votes"))
            rows[type].append(a.get("postproc").get("results")[j].get(type))
            j = j + 1
        res["question " + str(i)] = rows
        i = i + 1
    return res


class VisualizerView(TemplateView):
    template_name = "visualizer/visualizer.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get("voting_id", 0)

        try:
            r = mods.get("voting", params={"id": vid})
            c = mods.get("census", params={"voting_id": vid})
            context["voting"] = json.dumps(r[0])
            context["census"] = json.dumps(c)
        except:
            raise Http404

        return context
