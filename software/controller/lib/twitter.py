__author__ = 'Andrew Taylor'

import tweepy
import time

from pluginmodel import PluginPlaylist
from pluginmodel import Plugin

# TODO: Switch to logging not print() statements

# Twitter control is implemented by a special playlist.
# This playlist has only one item to start with - the traditional dance floor plugin,
#  and new items can be added as the tweets come in.
# Each plugin lasts a minimum of 5 seconds, but will remain on if it is the most recent one to be tweeted
#  and there are no further requests after it.

# TODO: Parse in mapping from file or configuration file
mapping = {
    "sinewave"      : "SineWaveVisualisationPlugin",
    "disco"         : "DiscoFloorVisualisationPlugin",
    "blobs"         : "SpeedingBlobsVisualisationPlugin",
    "spinningwheel" : "SpinningWheelVisualisationPlugin",
    "wavyblob"      : "WavyBlobVisualisationPlugin"
}

# Default minimum plugin duration in seconds
PLUGIN_DURATION_DEFAULT=6


class TwitterListener(tweepy.streaming.StreamListener):
    def __init__(self, our_twitter_handle, api=None, callback=None):
        self.our_twitter_handle = our_twitter_handle
        self.api = api
        self.callback = callback

        # If we can Tweet out, say that we have started
        if api is not None:
            self.api.update_status("Twitter listener started at %s" % time.time())

    # This is called when a new tweet appears on our timeline
    # status is an object with parsed out variables from the datastream (meaning that we don't need to
    #  parse the JSON ourselves).
    def on_status(self, status):
        print ("Status")

        # Sample tweet to us:
        # Status(contributors=None, truncated=False, text=u'@LED_Dance_Floor I see you have started up again', is_quote_status=False, in_reply_to_status_id=None, id=710946447370416132, favorite_count=0, _api=<tweepy.api.API object at 0x7fe61e2dd390>, author=User(follow_request_sent=None, profile_use_background_image=True, _json={u'follow_request_sent': None, u'profile_use_background_image': True, u'default_profile_image': False, u'id': 15562423, u'verified': False, u'profile_image_url_https': u'https://pbs.twimg.com/profile_images/666717744608501761/B5xfFqYn_normal.jpg', u'profile_sidebar_fill_color': u'DDEEF6', u'profile_text_color': u'333333', u'followers_count': 138, u'profile_sidebar_border_color': u'C0DEED', u'id_str': u'15562423', u'profile_background_color': u'C0DEED', u'listed_count': 9, u'profile_background_image_url_https': u'https://abs.twimg.com/images/themes/theme1/bg.png', u'utc_offset': 0, u'statuses_count': 3844, u'description': u'Parkrunner, Astrophotographer, lost descendant of Heath Robinson', u'friends_count': 349, u'location': u'Winchester', u'profile_link_color': u'0084B4', u'profile_image_url': u'http://pbs.twimg.com/profile_images/666717744608501761/B5xfFqYn_normal.jpg', u'following': None, u'geo_enabled': True, u'profile_banner_url': u'https://pbs.twimg.com/profile_banners/15562423/1430305578', u'profile_background_image_url': u'http://abs.twimg.com/images/themes/theme1/bg.png', u'name': u'AndyT', u'lang': u'en', u'profile_background_tile': False, u'favourites_count': 58, u'screen_name': u'fraz3alpha', u'notifications': None, u'url': None, u'created_at': u'Wed Jul 23 13:51:41 +0000 2008', u'contributors_enabled': False, u'time_zone': u'London', u'protected': False, u'default_profile': True, u'is_translator': False}, id=15562423, _api=<tweepy.api.API object at 0x7fe61e2dd390>, verified=False, profile_image_url_https=u'https://pbs.twimg.com/profile_images/666717744608501761/B5xfFqYn_normal.jpg', profile_sidebar_fill_color=u'DDEEF6', is_translator=False, geo_enabled=True, profile_text_color=u'333333', followers_count=138, protected=False, location=u'Winchester', default_profile_image=False, id_str=u'15562423', utc_offset=0, statuses_count=3844, description=u'Parkrunner, Astrophotographer, lost descendant of Heath Robinson', friends_count=349, profile_link_color=u'0084B4', profile_image_url=u'http://pbs.twimg.com/profile_images/666717744608501761/B5xfFqYn_normal.jpg', notifications=None, profile_background_image_url_https=u'https://abs.twimg.com/images/themes/theme1/bg.png', profile_background_color=u'C0DEED', profile_banner_url=u'https://pbs.twimg.com/profile_banners/15562423/1430305578', profile_background_image_url=u'http://abs.twimg.com/images/themes/theme1/bg.png', screen_name=u'fraz3alpha', lang=u'en', profile_background_tile=False, favourites_count=58, name=u'AndyT', url=None, created_at=datetime.datetime(2008, 7, 23, 13, 51, 41), contributors_enabled=False, time_zone=u'London', profile_sidebar_border_color=u'C0DEED', default_profile=True, following=False, listed_count=9), _json={u'contributors': None, u'truncated': False, u'text': u'@LED_Dance_Floor I see you have started up again', u'is_quote_status': False, u'in_reply_to_status_id': None, u'id': 710946447370416132, u'favorite_count': 0, u'source': u'<a href="http://twitter.com/download/android" rel="nofollow">Twitter for Android</a>', u'retweeted': False, u'coordinates': None, u'timestamp_ms': u'1458337816456', u'entities': {u'user_mentions': [{u'id': 710566689491050496, u'indices': [0, 16], u'id_str': u'710566689491050496', u'screen_name': u'LED_Dance_Floor', u'name': u'LED DiscoDanceFloor'}], u'symbols': [], u'hashtags': [], u'urls': []}, u'in_reply_to_screen_name': u'LED_Dance_Floor', u'id_str': u'710946447370416132', u'retweet_count': 0, u'in_reply_to_user_id': 710566689491050496, u'favorited': False, u'user': {u'follow_request_sent': None, u'profile_use_background_image': True, u'default_profile_image': False, u'id': 15562423, u'verified': False, u'profile_image_url_https': u'https://pbs.twimg.com/profile_images/666717744608501761/B5xfFqYn_normal.jpg', u'profile_sidebar_fill_color': u'DDEEF6', u'profile_text_color': u'333333', u'followers_count': 138, u'profile_sidebar_border_color': u'C0DEED', u'id_str': u'15562423', u'profile_background_color': u'C0DEED', u'listed_count': 9, u'profile_background_image_url_https': u'https://abs.twimg.com/images/themes/theme1/bg.png', u'utc_offset': 0, u'statuses_count': 3844, u'description': u'Parkrunner, Astrophotographer, lost descendant of Heath Robinson', u'friends_count': 349, u'location': u'Winchester', u'profile_link_color': u'0084B4', u'profile_image_url': u'http://pbs.twimg.com/profile_images/666717744608501761/B5xfFqYn_normal.jpg', u'following': None, u'geo_enabled': True, u'profile_banner_url': u'https://pbs.twimg.com/profile_banners/15562423/1430305578', u'profile_background_image_url': u'http://abs.twimg.com/images/themes/theme1/bg.png', u'name': u'AndyT', u'lang': u'en', u'profile_background_tile': False, u'favourites_count': 58, u'screen_name': u'fraz3alpha', u'notifications': None, u'url': None, u'created_at': u'Wed Jul 23 13:51:41 +0000 2008', u'contributors_enabled': False, u'time_zone': u'London', u'protected': False, u'default_profile': True, u'is_translator': False}, u'geo': None, u'in_reply_to_user_id_str': u'710566689491050496', u'lang': u'en', u'created_at': u'Fri Mar 18 21:50:16 +0000 2016', u'filter_level': u'low', u'in_reply_to_status_id_str': None, u'place': None}, coordinates=None, timestamp_ms=u'1458337816456', entities={u'user_mentions': [{u'id': 710566689491050496, u'indices': [0, 16], u'id_str': u'710566689491050496', u'screen_name': u'LED_Dance_Floor', u'name': u'LED DiscoDanceFloor'}], u'symbols': [], u'hashtags': [], u'urls': []}, in_reply_to_screen_name=u'LED_Dance_Floor', in_reply_to_user_id=710566689491050496, retweet_count=0, id_str=u'710946447370416132', favorited=False, source_url=u'http://twitter.com/download/android', user=User(follow_request_sent=None, profile_use_background_image=True, _json={u'follow_request_sent': None, u'profile_use_background_image': True, u'default_profile_image': False, u'id': 15562423, u'verified': False, u'profile_image_url_https': u'https://pbs.twimg.com/profile_images/666717744608501761/B5xfFqYn_normal.jpg', u'profile_sidebar_fill_color': u'DDEEF6', u'profile_text_color': u'333333', u'followers_count': 138, u'profile_sidebar_border_color': u'C0DEED', u'id_str': u'15562423', u'profile_background_color': u'C0DEED', u'listed_count': 9, u'profile_background_image_url_https': u'https://abs.twimg.com/images/themes/theme1/bg.png', u'utc_offset': 0, u'statuses_count': 3844, u'description': u'Parkrunner, Astrophotographer, lost descendant of Heath Robinson', u'friends_count': 349, u'location': u'Winchester', u'profile_link_color': u'0084B4', u'profile_image_url': u'http://pbs.twimg.com/profile_images/666717744608501761/B5xfFqYn_normal.jpg', u'following': None, u'geo_enabled': True, u'profile_banner_url': u'https://pbs.twimg.com/profile_banners/15562423/1430305578', u'profile_background_image_url': u'http://abs.twimg.com/images/themes/theme1/bg.png', u'name': u'AndyT', u'lang': u'en', u'profile_background_tile': False, u'favourites_count': 58, u'screen_name': u'fraz3alpha', u'notifications': None, u'url': None, u'created_at': u'Wed Jul 23 13:51:41 +0000 2008', u'contributors_enabled': False, u'time_zone': u'London', u'protected': False, u'default_profile': True, u'is_translator': False}, id=15562423, _api=<tweepy.api.API object at 0x7fe61e2dd390>, verified=False, profile_image_url_https=u'https://pbs.twimg.com/profile_images/666717744608501761/B5xfFqYn_normal.jpg', profile_sidebar_fill_color=u'DDEEF6', is_translator=False, geo_enabled=True, profile_text_color=u'333333', followers_count=138, protected=False, location=u'Winchester', default_profile_image=False, id_str=u'15562423', utc_offset=0, statuses_count=3844, description=u'Parkrunner, Astrophotographer, lost descendant of Heath Robinson', friends_count=349, profile_link_color=u'0084B4', profile_image_url=u'http://pbs.twimg.com/profile_images/666717744608501761/B5xfFqYn_normal.jpg', notifications=None, profile_background_image_url_https=u'https://abs.twimg.com/images/themes/theme1/bg.png', profile_background_color=u'C0DEED', profile_banner_url=u'https://pbs.twimg.com/profile_banners/15562423/1430305578', profile_background_image_url=u'http://abs.twimg.com/images/themes/theme1/bg.png', screen_name=u'fraz3alpha', lang=u'en', profile_background_tile=False, favourites_count=58, name=u'AndyT', url=None, created_at=datetime.datetime(2008, 7, 23, 13, 51, 41), contributors_enabled=False, time_zone=u'London', profile_sidebar_border_color=u'C0DEED', default_profile=True, following=False, listed_count=9), geo=None, in_reply_to_user_id_str=u'710566689491050496', lang=u'en', created_at=datetime.datetime(2016, 3, 18, 21, 50, 16), filter_level=u'low', in_reply_to_status_id_str=None, place=None, source=u'Twitter for Android', retweeted=False)

        # Sample reply tweet (like what we would post)
        # Status(contributors=None, truncated=False, text=u'@LED_Dance_Floor testing', is_quote_status=False, in_reply_to_status_id=710587755806527488, id=710947068580401152, favorite_count=0, _api=<tweepy.api.API object at 0x7fe61e2dd390>, author=User(follow_request_sent=None, profile_use_background_image=True, _json={u'follow_request_sent': None, u'profile_use_background_image': True, u'default_profile_image': True, u'id': 710566689491050496, u'verified': False, u'profile_image_url_https': u'https://abs.twimg.com/sticky/default_profile_images/default_profile_6_normal.png', u'profile_sidebar_fill_color': u'DDEEF6', u'profile_text_color': u'333333', u'followers_count': 2, u'profile_sidebar_border_color': u'C0DEED', u'id_str': u'710566689491050496', u'profile_background_color': u'F5F8FA', u'listed_count': 0, u'profile_background_image_url_https': u'', u'utc_offset': 0, u'statuses_count': 8, u'description': None, u'friends_count': 0, u'location': None, u'profile_link_color': u'2B7BB9', u'profile_image_url': u'http://abs.twimg.com/sticky/default_profile_images/default_profile_6_normal.png', u'following': None, u'geo_enabled': False, u'profile_background_image_url': u'', u'name': u'LED DiscoDanceFloor', u'lang': u'en-gb', u'profile_background_tile': False, u'favourites_count': 0, u'screen_name': u'LED_Dance_Floor', u'notifications': None, u'url': None, u'created_at': u'Thu Mar 17 20:41:15 +0000 2016', u'contributors_enabled': False, u'time_zone': u'London', u'protected': False, u'default_profile': True, u'is_translator': False}, id=710566689491050496, _api=<tweepy.api.API object at 0x7fe61e2dd390>, verified=False, profile_image_url_https=u'https://abs.twimg.com/sticky/default_profile_images/default_profile_6_normal.png', profile_sidebar_fill_color=u'DDEEF6', is_translator=False, geo_enabled=False, profile_text_color=u'333333', followers_count=2, protected=False, location=None, default_profile_image=True, id_str=u'710566689491050496', utc_offset=0, statuses_count=8, description=None, friends_count=0, profile_link_color=u'2B7BB9', profile_image_url=u'http://abs.twimg.com/sticky/default_profile_images/default_profile_6_normal.png', notifications=None, profile_background_image_url_https=u'', profile_background_color=u'F5F8FA', profile_background_image_url=u'', screen_name=u'LED_Dance_Floor', lang=u'en-gb', profile_background_tile=False, favourites_count=0, name=u'LED DiscoDanceFloor', url=None, created_at=datetime.datetime(2016, 3, 17, 20, 41, 15), contributors_enabled=False, time_zone=u'London', profile_sidebar_border_color=u'C0DEED', default_profile=True, following=False, listed_count=0), _json={u'contributors': None, u'truncated': False, u'text': u'@LED_Dance_Floor testing', u'is_quote_status': False, u'in_reply_to_status_id': 710587755806527488, u'id': 710947068580401152, u'favorite_count': 0, u'source': u'<a href="http://twitter.com/download/android" rel="nofollow">Twitter for Android</a>', u'retweeted': False, u'coordinates': None, u'timestamp_ms': u'1458337964564', u'entities': {u'user_mentions': [{u'id': 710566689491050496, u'indices': [0, 16], u'id_str': u'710566689491050496', u'screen_name': u'LED_Dance_Floor', u'name': u'LED DiscoDanceFloor'}], u'symbols': [], u'hashtags': [], u'urls': []}, u'in_reply_to_screen_name': u'LED_Dance_Floor', u'id_str': u'710947068580401152', u'retweet_count': 0, u'in_reply_to_user_id': 710566689491050496, u'favorited': False, u'user': {u'follow_request_sent': None, u'profile_use_background_image': True, u'default_profile_image': True, u'id': 710566689491050496, u'verified': False, u'profile_image_url_https': u'https://abs.twimg.com/sticky/default_profile_images/default_profile_6_normal.png', u'profile_sidebar_fill_color': u'DDEEF6', u'profile_text_color': u'333333', u'followers_count': 2, u'profile_sidebar_border_color': u'C0DEED', u'id_str': u'710566689491050496', u'profile_background_color': u'F5F8FA', u'listed_count': 0, u'profile_background_image_url_https': u'', u'utc_offset': 0, u'statuses_count': 8, u'description': None, u'friends_count': 0, u'location': None, u'profile_link_color': u'2B7BB9', u'profile_image_url': u'http://abs.twimg.com/sticky/default_profile_images/default_profile_6_normal.png', u'following': None, u'geo_enabled': False, u'profile_background_image_url': u'', u'name': u'LED DiscoDanceFloor', u'lang': u'en-gb', u'profile_background_tile': False, u'favourites_count': 0, u'screen_name': u'LED_Dance_Floor', u'notifications': None, u'url': None, u'created_at': u'Thu Mar 17 20:41:15 +0000 2016', u'contributors_enabled': False, u'time_zone': u'London', u'protected': False, u'default_profile': True, u'is_translator': False}, u'geo': None, u'in_reply_to_user_id_str': u'710566689491050496', u'lang': u'en', u'created_at': u'Fri Mar 18 21:52:44 +0000 2016', u'filter_level': u'low', u'in_reply_to_status_id_str': u'710587755806527488', u'place': None}, coordinates=None, timestamp_ms=u'1458337964564', entities={u'user_mentions': [{u'id': 710566689491050496, u'indices': [0, 16], u'id_str': u'710566689491050496', u'screen_name': u'LED_Dance_Floor', u'name': u'LED DiscoDanceFloor'}], u'symbols': [], u'hashtags': [], u'urls': []}, in_reply_to_screen_name=u'LED_Dance_Floor', in_reply_to_user_id=710566689491050496, retweet_count=0, id_str=u'710947068580401152', favorited=False, source_url=u'http://twitter.com/download/android', user=User(follow_request_sent=None, profile_use_background_image=True, _json={u'follow_request_sent': None, u'profile_use_background_image': True, u'default_profile_image': True, u'id': 710566689491050496, u'verified': False, u'profile_image_url_https': u'https://abs.twimg.com/sticky/default_profile_images/default_profile_6_normal.png', u'profile_sidebar_fill_color': u'DDEEF6', u'profile_text_color': u'333333', u'followers_count': 2, u'profile_sidebar_border_color': u'C0DEED', u'id_str': u'710566689491050496', u'profile_background_color': u'F5F8FA', u'listed_count': 0, u'profile_background_image_url_https': u'', u'utc_offset': 0, u'statuses_count': 8, u'description': None, u'friends_count': 0, u'location': None, u'profile_link_color': u'2B7BB9', u'profile_image_url': u'http://abs.twimg.com/sticky/default_profile_images/default_profile_6_normal.png', u'following': None, u'geo_enabled': False, u'profile_background_image_url': u'', u'name': u'LED DiscoDanceFloor', u'lang': u'en-gb', u'profile_background_tile': False, u'favourites_count': 0, u'screen_name': u'LED_Dance_Floor', u'notifications': None, u'url': None, u'created_at': u'Thu Mar 17 20:41:15 +0000 2016', u'contributors_enabled': False, u'time_zone': u'London', u'protected': False, u'default_profile': True, u'is_translator': False}, id=710566689491050496, _api=<tweepy.api.API object at 0x7fe61e2dd390>, verified=False, profile_image_url_https=u'https://abs.twimg.com/sticky/default_profile_images/default_profile_6_normal.png', profile_sidebar_fill_color=u'DDEEF6', is_translator=False, geo_enabled=False, profile_text_color=u'333333', followers_count=2, protected=False, location=None, default_profile_image=True, id_str=u'710566689491050496', utc_offset=0, statuses_count=8, description=None, friends_count=0, profile_link_color=u'2B7BB9', profile_image_url=u'http://abs.twimg.com/sticky/default_profile_images/default_profile_6_normal.png', notifications=None, profile_background_image_url_https=u'', profile_background_color=u'F5F8FA', profile_background_image_url=u'', screen_name=u'LED_Dance_Floor', lang=u'en-gb', profile_background_tile=False, favourites_count=0, name=u'LED DiscoDanceFloor', url=None, created_at=datetime.datetime(2016, 3, 17, 20, 41, 15), contributors_enabled=False, time_zone=u'London', profile_sidebar_border_color=u'C0DEED', default_profile=True, following=False, listed_count=0), geo=None, in_reply_to_user_id_str=u'710566689491050496', lang=u'en', created_at=datetime.datetime(2016, 3, 18, 21, 52, 44), filter_level=u'low', in_reply_to_status_id_str=u'710587755806527488', place=None, source=u'Twitter for Android', retweeted=False)

        # Who sent the tweet
        print ("Tweet from @%s" % status.user.screen_name)
        if status.user.screen_name == self.our_twitter_handle:
            print ("Not replying to ourselves")
            return True

        print ("Tweet contents: %s" % status.text)

        requested_plugin = None
        for plugin_eyecatcher in mapping:
            if plugin_eyecatcher in status.text.lower():
                requested_plugin_short_name = plugin_eyecatcher
                requested_plugin = mapping[plugin_eyecatcher]

        if requested_plugin is not None:
            # Reply
            reply_tweet = "@%s - Thank you for your interest, I'll be sure to pass on your request for %s" % \
                          (status.user.screen_name, requested_plugin_short_name)
            print ("Tweet Reply: %s" % reply_tweet)
            try:
                self.api.update_status(reply_tweet, status.id)
            except Exception as e:
                print(e)

            if self.callback is not None:
                try:
                    self.callback(plugin_name=requested_plugin, plugin_for=status.user.screen_name)
                except Exception as e:
                    print "Oops, something went wrong trying to callback with %s : %s" % (reply_tweet, e)

        else:
            # Reply
            reply_tweet = "@%s - Sorry, I can't work out what you wanted to display" % (status.user.screen_name)
            print ("Tweet Reply: %s" % reply_tweet)
            try:
                self.api.update_status(reply_tweet, status.id)
            except Exception as e:
                print(e)

class TwitterPlaylist(PluginPlaylist):

    # When we come back to this playlist (after going to the menu), we are potentially
    #  going to get into a pickle as it will try and re-start itself from the beginning.
    # Ideally we want the playlist to self-clean itself, only containing the plugins we
    #  haven't yet played, firstly so that it doesn't get overly long, but secondly so
    #  that we don't repeat a request.
    # N.B. Twitter will reject duplicate tweets, which will happen if we start the same
    #  plugin again, and try to send the same notification noting that we have started a
    #  plugin based ona  request.

    # Pre-seed a collection noting who this plugin was started for.
    # We need to clean this up as we go along
    who_for = {
        0: "myself"
    }

    # This playlist is similar, but not identical to the standard playlist. There are a
    #  few basic settings that we override, along with a number of methods.
    def __init__(self, plugins, details):

        required_parameters = ["username", "api_key", "api_secret", "access_token", "access_token_secret"]
        missing_parameters = []
        for param in required_parameters:
            if param not in details:
                missing_parameters.append(param)


        if len(missing_parameters) > 0:
            print ("Missing parameters for Twitter Playlist configuration, the following values have not been set:")
            for param in missing_parameters:
                print ("  %s" % param)

        # TODO: Automatically determine our Twitter handle from the API
        self.our_twitter_handle = details["username"]

        # Call the superclass to set up the basic playlist object
        # A USER playlist auto-advances
        super(TwitterPlaylist, self).__init__(PluginPlaylist.USER)
        # Set the loop mode to ONCE, indicating that the final plugin should continue
        #  to run even after it reaches its expiry
        self.loop_mode = "ONCE"
        self.details = details
        self.available_plugins = plugins

        # Add a stock plugin to start with, this will run until the first request comes in.
        # If we restart the dance floor code, it has no way of knowing what was, or wasn't,
        #  displayed previously, so will reset in this case. To get a new plugin displaying
        #  a tweet will have to be resent.

        # Fetch and add the DiscoFloorVisualisationPlugin plugin & object
        print ("Adding default plugin")
        default_plugin_name = "DiscoFloorVisualisationPlugin"
        default_plugin = self.available_plugins[default_plugin_name]
        print ("Default plugin: %s, %s" % (default_plugin_name, default_plugin))
        self.add_plugin(Plugin(default_plugin_name, default_plugin))

        # Start the listener which will stream the tweets directed at us.
        # This method must return, and currently it is configured to set up an asynchronous stream
        print ("Starting twitter listener")
        self.start_listener()

        # Initialisation complete

    # Starting the listener involves configuring a connection to Twitter, storing an API
    #  connection, and starting a stream in a non-blocking way
    def start_listener(self):
        # If we don't have any Twitter credentials, then we can't start a connection.
        # Should this throw an error if we don't have any credentials, or any connection?
        if self.details is not None:
            api_key = self.details["api_key"]
            api_secret = self.details["api_secret"]
            access_token = self.details["access_token"]
            access_token_secret = self.details["access_token_secret"]

            auth = tweepy.OAuthHandler(api_key, api_secret)
            auth.set_access_token(access_token, access_token_secret)

            # Create and store an API object so that we can tweet out messages
            self.api = tweepy.API(auth)
            listener = TwitterListener(self.our_twitter_handle, self.api, callback=self.add_entry)

            # Start the twitter stream
            twitterStream = tweepy.Stream(auth, listener)
            print ("Launching userstream")
            twitterStream.userstream(async=True)
            print ("Launched userstream")
        else:
            pass

    # Callback from the Twitter stream with the plugin name which will have been parsed from
    #  the message
    # TODO: take in a set of properties that may have been defined in the Tweet request
    def add_entry(self, plugin_name, plugin_for, plugin_duration=PLUGIN_DURATION_DEFAULT):
        print ("Adding plugin: %s as requested from Twitter" % plugin_name)
        plugin = self.available_plugins[plugin_name]
        if plugin is not None:
            print ("Adding plugin object for %s" % plugin_name)
            plugin_parameters = {"duration": plugin_duration}
            plugin_index = self.add_plugin(Plugin(plugin_name, plugin, plugin_parameters))
            self.who_for[plugin_index] = plugin_for
        else:
            print ("Unable to find plugin object for %s" % plugin_name)

    def start_plugin(self, index):
        super(TwitterPlaylist, self).start_plugin(index)
        # Tweet them to let them know we've started it for them

        if index > 0:
            # Skip sending a tweet for ourselves
            plugin_for = self.who_for[index]
            print ("Starting plugin %s for %s" % (index, plugin_for))
            msg = "Starting %s for @%s" % (self.plugins[index].plugin_name, plugin_for)
            try:
                self.api.update_status(msg)
            except Exception as e:
                print(e)


    # The splash screen of the Twitter playlist should be different to the regular playlist
    #  so that we know which one it is. It will also only exist once (unless we change the code
    #  to allow a set of Twitter playlists, attached to different Twitter accounts - in which case
    #  we will have other issues to fix too anyway)
    def draw_splash(self, canvas):
        # Black blue background
        canvas.set_colour((0, 0, 0))

        # Draw something representing Twitter in the middle
        # Draw a blue 'T' n the middle(ish)
        t_x = int(canvas.get_width()/2)-3
        t_y = int(canvas.get_height()/2)-4
        canvas.draw_text("T", (0, 0, 0xFF), t_x, t_y)
        return canvas

    # Override the string method so that we can be uniquely defined
    def __str__(self):
        string = "TwitterPlaylist for @%s - #%s : %s\n" % (self.our_twitter_handle, self.playlist_number, self.state)
        for idx, plugin in enumerate(self.get_plugins()):
            if idx == self.current_position:
                string += " >%s\n" % plugin
            else:
                string += "  %s\n" % plugin
        return string

    # TODO: Create a reuable method to catch Twitter errors when we tweet
    def send_tweet_and_catch_errors(self, message, in_reply_to=None):
        pass