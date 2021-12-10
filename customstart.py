from instapy import InstaPy
from instapy import smart_run
import random

tags = ['NFTS', 'wizardofoz', 'OpenSea', 'tinman', 'NFTArt', 'NFTCommunity', 'NFTCollector', 'DigitalArtists', 'solana', 'wizardofozcollection', 'polygon']
popularAcounts = ['cryptobullsociety', 'gogalagames', 'monaco_planet', 'apekidsclub', 'wizardofozfilm', 'wonderfulwizardofoz', 'tinmanofoz_', 'collectingoz']
photo_comments = ['Ozamatasm! @{} :muscle:', 'Oztastic! @{}']    # get list of all emoji's (:muscle:)

session = InstaPy(username='tinmania.io', 
                    password='tWx!25$dah', 
                    bypass_security_challenge_using='sms', 
                    headless_browser=False)

with smart_run(session):
    session.set_relationship_bounds(enabled=True, delimit_by_numbers=True, max_followers=1500, min_followers=25, min_following=50)

    session.unfollow_users(amount=35, nonFollowers=True, style="RANDOM", unfollow_after=42*60*60, sleep_delay=655)

    session.set_user_interact(amount=2, randomize=True, percentage=85, media='Photo')
    session.like_by_tags(tags, amount=3, interact=True)
    session.follow_user_followers(popularAcounts, amount=9, randomize=False, interact=True)

    session.set_do_comment(enabled = True, percentage = 90)
    session.set_comments(photo_comments, media = 'Photo')
    session.join_pods(topic='entertainment', engagement_mode='light')

    session.set_do_story(enabled = True, percentage = 1, simulate = True)
    session.story_by_tags(random.choice(tags, 5))