import getpass
import requests

from collections import defaultdict


def process_scores(regional_scores):
    # Print out the regions and the teams ordered by score
    for region, teams in regional_scores.items():
        print(f"Region: {region}")
        for team, score in dict(
            sorted(teams.items(), key=lambda item: item[1], reverse=True)
        ).items():
            print(f"{team}: {score}")
        print("\n")


def get_scores_by_region(ctfd_username, ctfd_password):
    regional_scores = defaultdict(dict)

    ctfd_session = requests.Session()
    ctfd_url = "https://cybersci.ctfd.io"

    # Request the login page so we can get the nonce
    login_page = ctfd_session.get(f"{ctfd_url}/login")
    nonce = login_page.text.split("csrfNonce': \"")[1].split('"')[0]

    # Combine the nonce with the username and password to get our session authenticated
    ctfd_session.post(
        f"{ctfd_url}/login",
        data={
            "name": ctfd_username,
            "password": ctfd_password,
            "_submit": "Submit",
            "nonce": nonce,
        },
        allow_redirects=False,
    )

    # Step one grab the teams
    teams = ctfd_session.get(f"{ctfd_url}/api/v1/teams").json()

    # The teams page caps at 50, so hopefully we can just ignore pagination
    for team in teams["data"]:
        team_name = team["name"]
        team_id = team["id"]
        team_region = ""
        for field in team["fields"]:
            # If a Region field is found, grab the value and we're done
            if field["name"] == "Region":
                team_region = field["value"]
                break
        # Now to get the team's score
        team_details = ctfd_session.get(f"{ctfd_url}/api/v1/teams/{team_id}").json()
        if "success" in team_details and team_details["success"] == True:
            team_score = team_details["data"]["score"]
            regional_scores[team_region][team_name] = team_score

    # Scores are collected, so send them off to do whatever
    process_scores(regional_scores)


if __name__ == "__main__":
    ctfd_username = input("CTFd Username: ")
    ctfd_password = getpass.getpass("CTFd Password: ")
    get_scores_by_region(ctfd_username, ctfd_password)
