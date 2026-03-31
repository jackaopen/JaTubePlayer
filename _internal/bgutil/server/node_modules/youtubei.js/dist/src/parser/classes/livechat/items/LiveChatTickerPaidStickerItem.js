import { YTNode } from '../../../helpers.js';
import { Parser } from '../../../index.js';
import Thumbnail from '../../misc/Thumbnail.js';
import NavigationEndpoint from '../../NavigationEndpoint.js';
export default class LiveChatTickerPaidStickerItem extends YTNode {
    static type = 'LiveChatTickerPaidStickerItem';
    id;
    author_external_channel_id;
    author_photo;
    start_background_color;
    end_background_color;
    duration_sec;
    full_duration_sec;
    show_item;
    show_item_endpoint;
    ticker_thumbnails;
    constructor(data) {
        super();
        this.id = data.id;
        this.author_external_channel_id = data.authorExternalChannelId;
        this.author_photo = Thumbnail.fromResponse(data.authorPhoto);
        this.start_background_color = data.startBackgroundColor;
        this.end_background_color = data.endBackgroundColor;
        this.duration_sec = data.durationSec;
        this.full_duration_sec = data.fullDurationSec;
        this.show_item = Parser.parseItem(data.showItemEndpoint?.showLiveChatItemEndpoint?.renderer);
        this.show_item_endpoint = new NavigationEndpoint(data.showItemEndpoint);
        this.ticker_thumbnails = data.tickerThumbnails.map((item) => ({
            thumbnails: Thumbnail.fromResponse(item),
            label: item?.accessibility?.accessibilityData?.label
        }));
    }
}
//# sourceMappingURL=LiveChatTickerPaidStickerItem.js.map