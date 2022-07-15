from django.http import JsonResponse
from common.json import ModelEncoder
from .models import Attendee, ConferenceVO
from django.views.decorators.http import require_http_methods
import json
from attendees.models import AccountVO

class ConferenceVODetailEncoder(ModelEncoder):
    model = ConferenceVO
    properties = ["name", "import_href"]


class AttendeeListEncoder(ModelEncoder):
    model = Attendee
    properties = ["name"]

@require_http_methods(["GET", "POST"])
def api_list_attendees(request, conference_vo_id=None):
    if request.method == "GET":
        attendees = Attendee.objects.filter(conference=conference_vo_id)
        return JsonResponse(
            attendees,
            encoder = AttendeeListEncoder,
            safe = False
        )
    else: #POST
        content = json.loads(request.body)
        try:
            conference = ConferenceVO.objects.get(id=conference_vo_id)
            content["conference"] = conference

            ## THIS CHANGES TO ConferenceVO
        except ConferenceVO.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400,
            )

        attendee = Attendee.objects.create(**content)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )
    """
    Lists the attendees names and the link to the attendee
    for the specified conference id.

    Returns a dictionary with a single key "attendees" which
    is a list of attendee names and URLS. Each entry in the list
    is a dictionary that contains the name of the attendee and
    the link to the attendee's information.

    {
        "attendees": [
            {
                "name": attendee's name,
                "href": URL to the attendee,
            },
            ...
        ]
    }
    """

    # response = []
    # attendees = Attendee.objects.all()
    # for attendee in attendees:
    #     response.append(
    #         {
    #             "name": attendee.name,
    #             "href": attendee.get_api_url(),
    #         }
    #     )
    # return JsonResponse({"attendees": response})
###################################################################

class AttendeeDetailEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "email",
        "name",
        "company_name",
        "created",
        "conference",
    ]
    encoders = {
        "conference": ConferenceVODetailEncoder()
    }

    def get_extra_data(self, o):
        count = AccountVO.objects.filter(email = o.email).count()
        if count > 0:
            return {
                "count": count,
                "has_account": True
            }
        else:
            return {
                "o.email": o.email,
                "count": count,
                "has_account": False
            }
        # Get the count of AccountVO objects with email equal to o.email
        # Return a dictionary with "has_account": True if count > 0
        # Otherwise, return a dictionary with "has_account": False

    # could technically use get_extra_data to specify all of the data you want 
    # to return but since you want to return all of the properties Conference has to 
    # answer you want to use and encoder to cut down on code. That's the point!!!

@require_http_methods(["GET", "PUT", "DELETE"])
def api_show_attendee(request, pk):
    if request.method == "GET":
        attendee = Attendee.objects.get(id=pk)
        return JsonResponse(
            attendee,
            encoder = AttendeeDetailEncoder,
            safe = False
        )
    elif request.method == "PUT":
        content = json.loads(request.body)
        try:
            if "conference" in content:
                #below is saying get the name and href from the id lookup im giving you
                conference = ConferenceVO.objects.get(id=content["conference"])
                content["conference"] = conference
        except ConferenceVO.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid Conference id"},
                status = 400
            )
        Attendee.objects.filter(id=pk).update(**content)
        attendee = Attendee.objects.get(id=pk)
        return JsonResponse(
            attendee,
            encoder = AttendeeDetailEncoder,
            safe = False
        )
    else: #DELETE
        count, _ = Attendee.objects.filter(id=pk).delete()
        return JsonResponse({"deleted": count > 0})
    """
    Returns the details for the Attendee model specified
    by the pk parameter.

    This should return a dictionary with email, name,
    company name, created, and conference properties for
    the specified Attendee instance.

    {
        "email": the attendee's email,
        "name": the attendee's name,
        "company_name": the attendee's company's name,
        "created": the date/time when the record was created,
        "conference": {
            "name": the name of the conference,
            "href": the URL to the conference,
        }
    }
    """



    # attendee = Attendee.objects.get(id=pk)
    # return JsonResponse(
    #     {
    #     "email": attendee.email,
    #     "name": attendee.name,
    #     "company_name": attendee.company_name,
    #     "created": attendee.created,
    #     "conference": {
    #         "name": attendee.conference.name,
    #         "href": attendee.conference.get_api_url(),    
    #         },
    #     }
    # )
