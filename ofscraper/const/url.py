initEP = "https://onlyfans.com/api2/v2/init"
LICENCE_URL = "https://onlyfans.com/api2/v2/users/media/{}/drm/{}/{}?type=widevine"


INDIVIDUAL_TIMELINE = "https://onlyfans.com/api2/v2/posts/{}?skip_users=all"
meEP = "https://onlyfans.com/api2/v2/users/me"
# earningsEP = "https://onlyfans.com/api2/v2/earnings/chart?startDate=2024-05-15 00:00:00&endDate=2024-06-13 21:07:10"
# earningsEP = "https://onlyfans.com/api2/v2/earnings/chart?startDate=2024-05-15%2000%3A00%3A00&endDate=2024-06-13%2021%3A53%3A20&withTotal=true&filter[total_count]=total_count&filter[total_amount]=total_amount&filter[subscribes_count]=subscribes_count&filter[subscribes_amount]=subscribes_amount&filter[tips_count]=tips_count&filter[tips_amount]=tips_amount&filter[messages_count]=messages_count&filter[messages_amount]=messages_amount&filter[post_count]=post_count&filter[post_amount]=post_amount&filter[stream_count]=stream_count&filter[stream_amount]=stream_amount&filter[tips_profile_count]=tips_profile_count&filter[tips_profile_amount]=tips_profile_amount&filter[tips_chat_count]=tips_chat_count&filter[tips_chat_amount]=tips_chat_amount&filter[tips_post_count]=tips_post_count&filter[tips_post_amount]=tips_post_amount&filter[tips_stream_count]=tips_stream_count&filter[tips_stream_amount]=tips_stream_amount&filter[tips_story_count]=tips_story_count&filter[tips_story_amount]=tips_story_amount"
earningsEP60D = "https://onlyfans.com/api2/v2/earnings/chart?startDate=2024-04-18%2000%3A00%3A00&endDate=2024-06-19%2019%3A30%3A53&withTotal=true&filter[total_count]=total_count&filter[total_amount]=total_amount&filter[subscribes_count]=subscribes_count&filter[subscribes_amount]=subscribes_amount&filter[tips_count]=tips_count&filter[tips_amount]=tips_amount&filter[messages_count]=messages_count&filter[messages_amount]=messages_amount&filter[post_count]=post_count&filter[post_amount]=post_amount&filter[stream_count]=stream_count&filter[stream_amount]=stream_amount&filter[tips_profile_count]=tips_profile_count&filter[tips_profile_amount]=tips_profile_amount&filter[tips_chat_count]=tips_chat_count&filter[tips_chat_amount]=tips_chat_amount&filter[tips_post_count]=tips_post_count&filter[tips_post_amount]=tips_post_amount&filter[tips_stream_count]=tips_stream_count&filter[tips_stream_amount]=tips_stream_amount&filter[tips_story_count]=tips_story_count&filter[tips_story_amount]=tips_story_amount"
balancesEp ="https://onlyfans.com/api2/v2/payouts/balances"
checkEp = "https://onlyfans.com/api2/v2/payouts/balances"
guestEP = "https://onlyfans.com/api2/v2/users/me/profile/stats?startDate=2024-06-10%2000%3A00%3A00&endDate=2024-06-19%2017%3A19%3A57&by=guests&filter[]=chart"
guestEP60D = "https://onlyfans.com/api2/v2/users/me/profile/stats?startDate=2024-04-18%2000%3A00%3A00&endDate=2024-06-19%2017%3A19%3A57&by=guests&filter[]=chart"
userEP60D = "https://onlyfans.com/api2/v2/users/me/profile/stats?startDate=2024-04-18T00%3A00%3A00&endDate=2024-06-16T17%3A42%3A03&by=users&filter%5B%5D=chart"
# fansAllEP60D = "https://onlyfans.com/api2/v2/users/me/stats/overview?startDate=2024-04-18%2000%3A00%3A00&endDate=2024-06-19%2018%3A42%3A22&by=fans"
fansAllEP60D = "https://onlyfans.com/api2/v2/subscriptions/subscribers/chart?startDate=2024-04-18%2000%3A00%3A00&endDate=2024-06-19%2019%3A29%3A02&by=total"
fansAllEP7D = "https://onlyfans.com/api2/v2/subscriptions/subscribers/chart?startDate=2024-06-10%2000%3A00%3A00&endDate=2024-06-19%2019%3A29%3A02&by=total"
fansNewEP60D = "https://onlyfans.com/api2/v2/subscriptions/subscribers/chart?startDate=2024-04-18%2000%3A00%3A00&endDate=2024-06-19%2020%3A55%3A02&by=new"

subscriptionsEP = "https://onlyfans.com/api2/v2/subscriptions/subscribes?offset={}&limit=10&type=all&format=infinite"


subscriptionsActiveEP = "https://onlyfans.com/api2/v2/subscriptions/subscribes?offset={}&limit=10&type=active&format=infinite"
subscriptionsExpiredEP = "https://onlyfans.com/api2/v2/subscriptions/subscribes?offset={}&limit=10&type=expired&format=infinite"

subscribeCountEP = "https://onlyfans.com/api2/v2/subscriptions/count/all"
sortSubscriptions = "https://onlyfans.com/api2/v2/lists/following/sort"
profileEP = "https://onlyfans.com/api2/v2/users/{}"

timelineEP = "https://onlyfans.com/api2/v2/users/{}/posts?limit=100&order=publish_date_asc&skip_users=all&skip_users_dups=1&pinned=0&format=infinite"
timelineNextEP = "https://onlyfans.com/api2/v2/users/{}/posts?limit=100&order=publish_date_asc&skip_users=all&skip_users_dups=1&afterPublishTime={}&pinned=0&format=infinite"

timelinePinnedEP = "https://onlyfans.com/api2/v2/users/{}/posts?skip_users=all&pinned=1&counters={}&format=infinite"
archivedEP = "https://onlyfans.com/api2/v2/users/{}/posts/archived?limit=100&order=publish_date_asc&skip_users=all&skip_users_dups=1&format=infinite"
archivedNextEP = "https://onlyfans.com/api2/v2/users/{}/posts/archived?limit=100&order=publish_date_asc&skip_users=all&skip_users_dups=1&afterPublishTime={}&format=infinite"

highlightsWithStoriesEP = (
    "https://onlyfans.com/api2/v2/users/{}/stories/highlights?limit=5&offset={}&unf=1"
)
highlightsWithAStoryEP = "https://onlyfans.com/api2/v2/users/{}/stories?unf=1"
storyEP = "https://onlyfans.com/api2/v2/stories/highlights/{}?unf=1"

messagesEP = "https://onlyfans.com/api2/v2/chats/{}/messages?limit=100&order=desc&skip_users=all&skip_users_dups=1"
messagesNextEP = "https://onlyfans.com/api2/v2/chats/{}/messages?limit=100&id={}&order=desc&skip_users=all&skip_users_dups=1"

favoriteEP = "https://onlyfans.com/api2/v2/posts/{}/favorites/{}"
postURL = "https://onlyfans.com/{}/{}"

DIGITALCRIMINALS = (
    "https://raw.githubusercontent.com/DATAHOARDERS/dynamic-rules/main/onlyfans.json"
)

# DEVIINT = "https://raw.githubusercontent.com/deviint/onlyfans-dynamic-rules/main/dynamicRules.json"
# https://raw.githubusercontent.com/datawhores/onlyfans-dynamic-rules/main/dynamicRules.json
# DEVIINT = "https://raw.githubusercontent.com/datawhores/onlyfans-dynamic-rules/main/dynamicRules.json"
# DEVIINT = "https://raw.githubusercontent.com/deviint/onlyfans-dynamic-rules/b6b1c1ae3910ed6a8bb282197a1c7dfb732fb82f/dynamicRules.json"
# DEVIINT = "https://raw.githubusercontent.com/datawhores/onlyfans-dynamic-rules/new/dynamicRules.json"
DEVIINT = "https://raw.githubusercontent.com/riley-access-labs/onlyfans-dynamic-rules-1/patch-1/dynamicRules.json"
SNEAKY = "https://raw.githubusercontent.com/SneakyOvis/onlyfans-dynamic-rules/main/rules.json"

donateEP = "https://www.buymeacoffee.com/excludedBittern"

purchased_contentEP = "https://onlyfans.com/api2/v2/posts/paid?limit=100&skip_users=all&format=infinite&offset={}&user_id={}"
purchased_contentALL = "https://onlyfans.com/api2/v2/posts/paid?limit=100&skip_users=all&format=infinite&offset={}"

highlightSPECIFIC = "https://onlyfans.com/api2/v2/stories/highlights/{}"
storiesSPECIFIC = "https://onlyfans.com/api2/v2/stories/{}"
messageSPECIFIC = "https://onlyfans.com/api2/v2/chats/{}/messages?limit=10&order=desc&skip_users=all&firstId={}"
messageTableSPECIFIC = "https://onlyfans.com/my/chats/{}/?id={}"

labelsEP = "https://onlyfans.com/api2/v2/users/{}/labels?limit=100&offset={}&order=desc&non-empty=1"
labelledPostsEP = "https://onlyfans.com/api2/v2/users/{}/posts?limit=100&offset={}&order=publish_date_desc&skip_users=all&counters=0&format=infinite&label={}"

listEP = "https://onlyfans.com/api2/v2/lists?offset={}&skip_users=all&limit=100&format=infinite"
listusersEP = (
    "https://onlyfans.com/api2/v2/lists/{}/users?offset={}&limit=100&format=infinite"
)
