from django.shortcuts import render, redirect
import requests
import logging

logger = logging.getLogger(__name__)

# Create your views here.
def home(request):
    logger.debug("homepage visited")
    return render(request, "home.html")


def search(request):

    # If the request method is not POST, redirect to the home page
    if request.method != "POST":
        logger.info(
            f"redirecting '{request.method}' request to '{request.path}' to '/'",
        )
        return redirect("/")

    # Get the search query
    query = request.POST.get("q", "")

    if not query:
        logger.info("search query is empty. Redirecting to /")
        return redirect("/")

    context = {"query": query}
    logger.info(f"incoming search query for '{query}'", extra=context)

    try:
        # Pass the search query to the Nominatim API to get a location
        location = requests.get(
            "https://nominatim.openstreetmap.org/search",
            {"q": query, "format": "json", "limit": "1"},
        ).json()

        logger.debug("Nominatim API response", extra={**context, "location": location})

        # If a location is found, pass the coordinate to the Time API to get the current time
        if location:
            coordinate = [location[0]["lat"], location[0]["lon"]]

            time = requests.get(
                "https://timeapi.io/api/Time/current/coordinate",
                {"latitude": coordinate[0], "longitude": coordinate[1]},
            )

            logger.debug("Time API response", extra={**context, "time": time.json()})
            logger.info(
                f"Search query for '{query}' succeeded without errors", extra=context
            )

            return render(
                request, "success.html", {"location": location[0], "time": time.json()}
            )

        # If a location is NOT found, return the error page
        else:
            logger.info(f"location '{query}' not found", extra=context)
            return render(request, "fail.html")
    except Exception as error:
        logger.exception(error, extra=context)
        return render(request, "500.html")
