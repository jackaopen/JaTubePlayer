import Thumbnail from './misc/Thumbnail.js';
import { YTNode } from '../helpers.js';
export default class ChannelMetadata extends YTNode {
    static type = 'ChannelMetadata';
    title;
    description;
    url;
    rss_url;
    vanity_channel_url;
    external_id;
    is_family_safe;
    keywords;
    avatar;
    music_artist_name;
    available_countries;
    android_deep_link;
    android_appindexing_link;
    ios_appindexing_link;
    constructor(data) {
        super();
        this.title = data.title;
        this.description = data.description;
        this.url = data.channelUrl;
        this.rss_url = data.rssUrl;
        this.vanity_channel_url = data.vanityChannelUrl;
        this.external_id = data.externalId;
        this.is_family_safe = data.isFamilySafe;
        this.keywords = data.keywords;
        this.avatar = Thumbnail.fromResponse(data.avatar);
        // Can be an empty string sometimes, so we need the extra length check
        this.music_artist_name = typeof data.musicArtistName === 'string' && data.musicArtistName.length > 0 ? data.musicArtistName : undefined;
        this.available_countries = data.availableCountryCodes;
        this.android_deep_link = data.androidDeepLink;
        this.android_appindexing_link = data.androidAppindexingLink;
        this.ios_appindexing_link = data.iosAppindexingLink;
    }
}
//# sourceMappingURL=ChannelMetadata.js.map