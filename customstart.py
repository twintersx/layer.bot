from instapy import InstaPy
from instapy import smart_run
import random

tags = ['NFTS', 'BoredApeYachtClub', 'OpenSea', 'ETH', 'NFTArt', 'NFTCommunity', 'NFTCollector', 'DigitalArtists']
popularAcounts = ['boredapeyachtclub', 'rtfktstudios', 'cryptobullsociety', 'gogalagames', 'desperateapewives', 'monaco_planet', 'apekidsclub']
photo_comments = ['Amazing! @{} :muscle:', 'Awesome! @{}']    # get list of all emoji's (:muscle:)

session = InstaPy(username='tinmania.io', 
                    password='tWx!25$dah', 
                    bypass_security_challenge_using='sms', 
                    headless_browser=False)

with smart_run(session):
    session.set_relationship_bounds(enabled=True, delimit_by_numbers=True, max_followers=2500, min_followers=25, min_following=50)

    session.like_by_tags(random.sample(tags, 1), amount=random.randint(5, 10), interact=True)
    session.set_user_interact(amount=1, randomize=True, percentage=90, media='Photo')
    session.follow_user_followers(popularAcounts, amount=2, randomize=False, interact=True)

    session.set_do_comment(enabled = True, percentage = 35)
    session.set_comments(photo_comments, media = 'Photo')
    session.join_pods(topic='entertainment', engagement_mode='light')

    session.set_do_story(enabled = True, percentage = 1, simulate = True)
    session.story_by_tags(tags)

    session.unfollow_users(amount=15, InstapyFollowed=(True, "nonfollowers"), style="FIFO", unfollow_after=12 * 60 * 60, sleep_delay=601)  # change to "all" to remove all