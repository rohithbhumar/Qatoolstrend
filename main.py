import json, os
from pprint import pprint
import streamlit as st
import plotly.express as px
import pandas as pd
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from copies_data_stargazers import *

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# List of top automation tools
repos = [
    "SeleniumHQ/selenium",
    "cypress-io/cypress",
    "webdriverio/webdriverio",
    "microsoft/playwright",
    "appium/appium"
    # Add more repositories as needed
]

def fetch_repo_data(repo_name):
    url = f"https://api.github.com/repos/{repo_name}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code


# Function to fetch stargazers data
def fetch_stargazers(repo_name):
    url = f"https://api.github.com/repos/{repo_name}/stargazers"
    headers = {
        'Accept': 'application/vnd.github.v3.star+json',
        'Authorization': f'token {GITHUB_TOKEN}'
    }
    params = {'per_page': 100}  # Adjust as needed for rate limits and performance
    stargazers = []

    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            resp_list = response.json()
            for dicts in resp_list:
                starred_at = dicts['starred_at']
                # Only append dates from the past 5 years
                if any(year in starred_at for year in
                       ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"]):
                    stargazers.append(starred_at)
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                url = None

    return stargazers


# pprint(fetch_stargazers("SeleniumHQ/selenium"))
# pprint(fetch_stargazers("cypress-io/cypress"))
# pprint(fetch_stargazers("webdriverio/webdriverio"))
# stars_list = fetch_stargazers("appium/appium")
# pprint(stars_list)

# # Save stars_list to a JSON file
# with open('stars_list.json', 'w') as f:
#     json.dump(stars_list, f)

# pprint(fetch_stargazers("microsoft/playwright"))


# def process_stargazers(stargazers):
#     star_dates = [datetime.strptime(star, '%Y-%m-%dT%H:%M:%SZ') for star in stargazers]
#     # print(star_dates)
#     star_years = [date.year for date in star_dates]
#     # print(star_years)
#     # print(star_years.count(2020)+star_years.count(2021)+star_years.count(2022)+star_years.count(2023)+star_years.count(2024))
#
#     y_2015_count = star_years.count(2015)
#     y_2016_count = star_years.count(2016)
#     y_2017_count = star_years.count(2017)
#     y_2018_count = star_years.count(2018)
#     y_2019_count = star_years.count(2019)
#     y_2020_count = star_years.count(2020)
#     y_2020_count = star_years.count(2020)
#     y_2021_count = star_years.count(2021)
#     y_2022_count = star_years.count(2022)
#     y_2023_count = star_years.count(2023)
#     y_2024_count = star_years.count(2024)
#     y_2025_count = star_years.count(2025)
#     print(y_2020_count)
#     # repeated_items = list(set([item for item in star_years if star_years.count(item) > 1]))
#     # print("Repeated items:", repeated_items)
def process_stargazers(stargazers):
    star_dates = [datetime.strptime(star, '%Y-%m-%dT%H:%M:%SZ') for star in stargazers]
    star_years = [date.year for date in star_dates]

    # Get the star count for the past 5 years
    current_year = datetime.now().year
    years = list(range(current_year - 10 + 1, current_year + 1))
    print(years)
    star_count_by_year = {year: 0 for year in years}

    for year in star_years:
        # star_count_by_year[year] = star_years.count(year)
        if year in star_count_by_year:
            star_count_by_year[year] += 1

    return star_count_by_year

# {2015: 1556, 2016: 2621, 2017: 3425, 2018: 3872, 2019: 3470, 2020: 3020, 2021: 3058, 2022: 3182, 2023: 3541, 2024: 1220}
# print(process_stargazers(stargazers=copies_data_stargazers.stargazers_5_year_data))


def parse_response(full_response):
    parsed_dict = {}

    # Use the .get() method to safely access dictionary keys and provide default values
    image = full_response.get('organization', {}).get('avatar_url', 'No Image Available')
    repo_name = full_response.get('full_name', 'No Repository Name')
    git_url = full_response.get('git_url', 'No Git URL')
    website = full_response.get('homepage', 'No Website')
    stars = full_response.get('stargazers_count', 0)
    forks = full_response.get('forks_count', 0)

    parsed_dict["avatar"] = image
    parsed_dict["repo_name"] = repo_name
    parsed_dict["git_url"] = git_url
    parsed_dict["website"] = website
    parsed_dict["stars"] = stars
    parsed_dict["forks"] = forks

    return parsed_dict

# parsed = parse_response(fetch_repo_data("SeleniumHQ/selenium"))
# print(parsed)

# Main function to display the Streamlit app

# List of top automation tools with their predefined stargazer data
repos_data = {
    "SeleniumHQ/selenium": selenium_10_year_data,
    "cypress-io/cypress": cypress_10_year,
    "webdriverio/webdriverio": webdriverio_10_year_stars,
    "microsoft/playwright": playwright_10_year_stars,
    "appium/appium": appium_10_year_stars,
}

def main():
    st.title("Top 5 Open Source Automation Tools")

    st.info(f"Data showing the GitHub STARS trends over the last 10 years.", icon="🌟")

    repo_data = []
    all_star_data = []

    for repo, stargazers in repos_data.items():
        response = fetch_repo_data(repo)
        parsed_data = parse_response(response)
        print(parsed_data)
        repo_data.append(parsed_data)
        
        star_count_by_year = process_stargazers(stargazers)
        
        for year, count in star_count_by_year.items():
            all_star_data.append({
                "repository": repo,
                "year": year,
                "stars": count,
                "avatar": parsed_data["avatar"]
            })
    # Convert to DataFrame for plotting
    df_trend = pd.DataFrame(all_star_data)

    # Plotting the historical trend
    fig = px.line(df_trend, x='year', y='stars', color='repository', title='GitHub Stars over past 10 years for Top Open Source Automation Tools')
    st.plotly_chart(fig)

    # Displaying repository avatars
    # st.write("Repository Avatars:")

    st.write("Repository Details:")
    for repo in repo_data:
        col1, col2 = st.columns([1, 3])
        with col1:
            if repo["avatar"] != 'No Image Available':
                st.image(repo["avatar"], caption=repo["repo_name"], width=100)
        with col2:
            st.write(f"**Repository:** {repo['repo_name']}")
            st.write(f"**Stars:** {repo['stars']}")
            st.write(f"**Forks:** {repo['forks']}")


if __name__ == "__main__":
    main()
