from django.shortcuts import render, redirect
import requests

# Create your views here.
def home(request):
    return render(request, "home.html")


def search(request):

    # If the request method is not POST, redirect to the home page
    if request.method != "POST":
        return redirect("/")

    # Get the search query
    query = request.POST.get("q", "")

    if not query:
        return redirect("/")

    try:
        # Pass the search query to the Nominatim API to get a location
        location = requests.get(
            "https://nominatim.openstreetmap.org/search",
            {"q": query, "format": "json", "limit": "1"},
        ).json()

        # If a location is found, pass the coordinate to the Time API to get the current time
        if location:
            coordinate = [location[0]["lat"], location[0]["lon"]]

            time = requests.get(
                "https://timeapi.io/api/Time/current/coordinate",
                {"latitude": coordinate[0], "longitude": coordinate[1]},
            )

            return render(
                request, "success.html", {"location": location[0], "time": time.json()}
            )

        # If a location is NOT found, return the error page
        else:
            return render(request, "fail.html")
    except Exception as error:
        return render(request, "500.html")
