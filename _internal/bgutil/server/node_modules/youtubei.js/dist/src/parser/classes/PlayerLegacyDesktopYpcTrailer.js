import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import YpcTrailer from './YpcTrailer.js';
export default class PlayerLegacyDesktopYpcTrailer extends YTNode {
    static type = 'PlayerLegacyDesktopYpcTrailer';
    video_id;
    title;
    thumbnail;
    offer_headline;
    offer_description;
    offer_id;
    offer_button_text;
    video_message;
    trailer;
    constructor(data) {
        super();
        this.video_id = data.trailerVideoId;
        this.title = data.itemTitle;
        this.thumbnail = data.itemThumbnail;
        this.offer_headline = data.offerHeadline;
        this.offer_description = data.offerDescription;
        this.offer_id = data.offerId;
        this.offer_button_text = data.offerButtonText;
        this.video_message = data.fullVideoMessage;
        this.trailer = Parser.parseItem(data.ypcTrailer, YpcTrailer);
    }
}
//# sourceMappingURL=PlayerLegacyDesktopYpcTrailer.js.map