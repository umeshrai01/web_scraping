import requests
import pandas as pd


access_token = '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'
headers = {'Authorization': f'token {access_token}'}


search_users_url = 'https://api.github.com/search/users'
user_details_url = 'https://api.github.com/users/{}'
repos_url_template = 'https://api.github.com/users/{}/repos'


users_data = []
repositories = []


def clean_company(company):
    if company:
        company = company.lstrip('@').strip().upper()
    return company or ""


params = {
    'q': 'location:Bangalore followers:>100',
    'per_page': 100
}
page = 1
while True:
    response = requests.get(search_users_url, headers=headers, params={**params, 'page': page})
    users = response.json().get('items', [])
    
    if not users:
        break
    
    for user in users:
        user_login = user['login']
        user_response = requests.get(user_details_url.format(user_login), headers=headers)
        user_detail = user_response.json()
        

        company_cleaned = clean_company(user_detail.get("company", ""))
        
        user_info = {
            "login": user_detail.get("login", ""),
            "name": user_detail.get("name", ""),
            "company": company_cleaned,
            "location": user_detail.get("location", ""),
            "email": user_detail.get("email", ""),
            "hireable": user_detail.get("hireable", ""),
            "bio": user_detail.get("bio", ""),
            "public_repos": user_detail.get("public_repos", 0),
            "followers": user_detail.get("followers", 0),
            "following": user_detail.get("following", 0),
            "created_at": user_detail.get("created_at", "")
        }
        users_data.append(user_info)
        
        repo_page = 1
        user_repos = 0
        while user_repos < 500:
            repo_response = requests.get(repos_url_template.format(user_login), headers=headers, params={
                'per_page': 100,
                'page': repo_page,
                'sort': 'updated'  # Fetch most recent repos
            })
            repos_data = repo_response.json()
            
            if not repos_data:
                break
            
            for repo in repos_data:
                repo_info = {
                    "login": user_login,
                    "full_name": repo.get("full_name", ""),
                    "created_at": repo.get("created_at", ""),
                    "stargazers_count": repo.get("stargazers_count", 0),
                    "watchers_count": repo.get("watchers_count", 0),
                    "language": repo.get("language", ""),
                    "has_projects": repo.get("has_projects", False),
                    "has_wiki": repo.get("has_wiki", False),
                    "license_name": repo.get("license", {}).get("key", "")
                }
                repositories.append(repo_info)
                user_repos += 1
                if user_repos >= 500:
                    break
            
            repo_page += 1

    page += 1


users_df = pd.DataFrame(users_data)
users_df.to_csv('users.csv', index=False)

repos_df = pd.DataFrame(repositories)
repos_df.to_csv('repositories.csv', index=False)
