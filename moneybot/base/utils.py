

def get_members(config_members, slack_users):
    """Get all the Slack users. Filter out bots and deleted ones."""
    users = {}
    for u in slack_users:
        if not u.get('deleted', False) and not u.get('is_bot', False):
            username = u['name']
            names = config_members.get(username)
            if names is not None:
                users['@' + username] = [n.lower() for n in names]
    return users

