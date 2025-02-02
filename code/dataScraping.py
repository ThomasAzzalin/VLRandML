import requests
import bs4 as bs
import re
from datetime import datetime, timedelta
import os
from csv import DictWriter

def extract_the_tournament_urls(reg):
    """
    Extract all the URLs from the file containing the tournaments. {tournaments.txt}
    :return: A list containing all the URLs in the specified file.
    """
    with open(f'.\\{reg}\\tournaments.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

def extract_match_links(tournament_url):
    """
    Extract all match links from a tournament page.
    This function takes the URL of a tournament page, fetches its content,
    and parses it to extract all match links that have a specific class pattern.

        :param tournament_url: The URL of the tournament page.
        :return: A list of match URLs found on the tournament page.
    """
    # Send a GET request to the tournament URL
    response = requests.get(tournament_url)
    page_content = response.text

    # Parse the HTML content using BeautifulSoup
    soup = bs.BeautifulSoup(page_content, features='html.parser')

    # Use regex to match the target class pattern
    target_classes = re.compile(r"^wf-module-item match-item")
    links = soup.find_all(name="a", class_=target_classes)

    # Extract and return the href attributes of all matching links
    return [link.get("href") for link in links]

def print_matches_urls(urls, reg):
    with open(f".\\{reg}\\matchesLinks.txt", "a") as file:
        urls = [f'https://www.vlr.gg{url}\n' for url in urls]
        file.writelines(urls)

def travel_back_in_time(date, days):
    """
    Generate a date by subtracting a specified number of days.

    This function is useful for constructing URLs where you need
    a start and end date range based on a given date.
        :param date: The date the match was played (format: 'YYYY-MM-DD').
        :param days: How many days should we go back?
        :return: The date minus the specified number of days (format: 'YYYY-MM-DD').
    """
    date_parts = date.split(' ')
    date_format = datetime.strptime(date_parts[0], "%Y-%m-%d")
    new_date = date_format - timedelta(days)
    return new_date.strftime("%Y-%m-%d")

def compose_team_stats_url(url_team, date_start, date_end):
    """
    Compose a full URL for team stats based on the team URL, start date, and end date.
        :param url_team: The relative URL of the team (e.g: "/team/1184/fut-esports/").
        :param date_start: The start date for the range (format: 'YYYY-MM-DD').
        :param date_end: The end date for the range (format: 'YYYY-MM-DD').
        :return: A string containing the full URL for the team's stats page in the chosen range.
    """
    base_url = "https://www.vlr.gg/"
    url_parts = url_team.strip('/').split('/')
    team_id = url_parts[1]
    team_name = url_parts[2]
    return f"{base_url}team/stats/{team_id}/{team_name}/?event_id=all&date_start={date_start}&date_end={date_end}"

def extract_team_stats(base_team_url, date_start, date_end):
    """
    Extract and calculate mean values from a team's stats page.

    This function fetches the team stats page for a specific date range, extracts
    numeric values from specific elements, and calculates the means for three columns.

    :param base_team_url: The base team URL (e.g., "/team/1184/fut-esports/").
    :param date_start: The start date (format 'YYYY-MM-DD').
    :param date_end: The end date (format 'YYYY-MM-DD').
    :return: A tuple containing the means of the three columns (mean1, mean2, mean3).
    """
    # Compose the stats URL
    url_team = compose_team_stats_url(base_team_url, date_start, date_end)

    # Fetch the page content
    response = requests.get(url_team)
    page_content = response.text

    # Parse the HTML content
    soup = bs.BeautifulSoup(page_content, features='html.parser')
    percentages = soup.find_all(name="div", class_="mod-first mod-highlight")

    # Extract and clean numeric values
    extracted_values = [per.text.strip() for per in percentages]
    numeric_values = [
            float(val.strip('%'))
            for val in extracted_values
            if val.replace('%', '').isdigit()
            ]

    # Divide values into three columns
    try:
        c_1 = numeric_values[::3]
        c_2 = numeric_values[1::3]
        c_3 = numeric_values[2::3]

        # Calculate and return the means
        mean1 = sum(c_1) / len(c_1)
        mean2 = sum(c_2) / len(c_2)
        mean3 = sum(c_3) / len(c_3)

        return mean1, mean2, mean3

    except Exception:
        return 0, 0, 0

def extract_date_match(soup):
    """
    Extracts the match date from a BeautifulSoup object.
    This function looks for a `div` element with the class `'moment-tz-convert'`
    and retrieves the value of its `data-utc-ts` attribute. The function returns
    only the date part (e.g., "2024-06-18") from the `data-utc-ts` value.
    :param soup: A BeautifulSoup object containing the HTML content of the page.
    :return: The match date and time as a string (e.g., "2024-06-18 14:00:00").
    """
    return soup.find(name="div", class_='moment-tz-convert').get('data-utc-ts').split(' ')[0] #e.g. 2024-06-18 14:00:00

def extract_teams(soup):
    """
       Extracts the team URLs from a BeautifulSoup object.
       This function searches for all anchor (`<a>`) elements whose class attribute match the specified pattern.
       The pattern is defined as those elements whose class begins with 'match-header-link wf-link-hover mod-',
       and it returns a list of the href attributes of those elements, which represent the URLs of the teams.
       :param soup: A BeautifulSoup object containing the HTML content of the page.
       :return: A list of URLs (as strings) that correspond to the teams.
       """
    class_pattern = re.compile(r"^match-header-link wf-link-hover mod-")
    URLs = soup.find_all(name="a", class_=class_pattern)
    return [url.get("href") for url in URLs]

def has_team_a_won(soup):
    """
        Determines whether Team A has won the match based on the score.
        This function looks for `span` elements with the class that match the pattern `^match-header-vs-score`,
        which represents the scores of the two teams. It compares the first and third elements
        :param soup: A BeautifulSoup object containing the HTML content of the page.
        :return: 1 if Team A has won, 0 if Team A has lost.
        """
    target_classes = re.compile(r"^match-header-vs-score")
    scores = soup.find_all(name="span", class_=target_classes)
    if (scores[0].text > scores[2].text):
        return 1
    else:
        return 0

def extract_info_match(url_match, reg):
    """
        Extracts match details from a given match URL, processes the data, and stores it in a CSV file.
        This function performs several steps to extract match information:
        - Retrieves the match date and splits it into date and time components.
        - Extracts the URLs of the two teams involved in the match.
        - Determines if Team A has won the match.
        - Calculates the date range (start and end) based on the match date.
        - Extracts team statistics for both teams within the specified date range.
        - Adds the extracted data to a CSV file.

        :param url_match: The URL of the match from which information needs to be extracted.
        :return: None
    """
    response = requests.get(url_match)
    page_content = response.text
    soup = bs.BeautifulSoup(page_content, features='html.parser')

    date = extract_date_match(soup)
    date_parts = date.split(' ')
    url_teams = extract_teams(soup)
    date_start = travel_back_in_time(date, 90)
    date_end = date_parts[0]
    team_a_stats = extract_team_stats(url_teams[0], date_start, date_end)
    team_b_stats = extract_team_stats(url_teams[1], date_start, date_end)

    row = {"team_a_general_win": team_a_stats[0],
          "team_a_atk_win": team_a_stats[1],
          "team_a_def_win": team_a_stats[2],
          "team_b_general_win": team_b_stats[0],
          "team_b_atk_win": team_b_stats[1],
          "team_b_def_win": team_b_stats[2],
          "team_a_won": has_team_a_won(soup),
          "date_match": date_parts[0],
          "url_match": url_match
                  }
    return row

def add_rows_csv(rows, reg):
    field_names = ["team_a_general_win",
                  "team_a_atk_win",
                  "team_a_def_win",
                  "team_b_general_win",
                  "team_b_atk_win",
                  "team_b_def_win",
                  "team_a_won",
                  "date_match",
                  "url_match"]
    with open(f'.\\{reg}\\data_set_unfiltered.csv', 'w', newline='') as csvfile:
        dictwriter_object = DictWriter(csvfile, fieldnames=field_names)
        dictwriter_object.writeheader()
        dictwriter_object.writerows(rows)
        csvfile.close()

def count_rows(reg):
    path = f'.\\{reg}\\matchesLinks.txt'
    with open(path, 'r') as file:
        lines = file.readlines()
        return len(lines)

if __name__ == '__main__':
    reg = input("Insert the region you want to save the data: ")
    if os.path.exists(f"{reg}\\matchesLinks.txt"):
        os.remove(f".\\{reg}\\matchesLinks.txt")
    url_tournemants = extract_the_tournament_urls(reg)

    for url in url_tournemants:
        urls_match = extract_match_links(url)
        print_matches_urls(urls_match, reg)

    with open(f'.\\{reg}\\matchesLinks.txt', 'r') as file:
        all_matches_urls = file.readlines()
        all_matches_urls = [url.strip("\n") for url in all_matches_urls]

    total_rows = count_rows(reg)
    progress_increment = total_rows / 100
    rows = list()
    i = 0
    for url in all_matches_urls:
        rows.append(extract_info_match(url, reg))
        progress = (i + 1) / total_rows * 100
        print(f"Progress: {progress:.2f}%")
        i += 1

    add_rows_csv(rows, reg)